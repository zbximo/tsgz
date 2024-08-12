# -*- encoding: utf-8 -*-
# @ModuleName: EventCls
# @Author: ximo
# @Time: 2024/5/14 14:53
import time

import paddlenlp
from modelscope import pipeline
from paddlenlp import Taskflow
import config
from pymilvus import MilvusClient, DataType
from BCEmbedding import EmbeddingModel, RerankerModel
from itertools import chain


class EventCls():
    def __init__(self):

        self.client = None
        self.collection_name = None
        self.bce_emb_model = EmbeddingModel(model_name_or_path=config.MODEL_CONFIG["bce-embedding-base_v1"],
                                            device="cuda:1")
        self.bce_reranker_model = RerankerModel(model_name_or_path=config.MODEL_CONFIG["bce-reranker-base_v1"],
                                                device="cuda:1")

    def insert_milvus(self, plan_id, data, is_news=True):
        """

        :param plan_id:
        :param data: [{}]
        :param is_news:
        :return:
        """
        if is_news:
            data_t = [i["title"] + i["content"] for i in data]
        else:
            data_t = [i["title"] for i in data]
        data_emb = self.bce_emb_model.encode(data_t).tolist()
        for idx, i in enumerate(data):
            i["embedding"] = data_emb[idx]
        self.client = MilvusClient(
            uri="http://10.63.146.221:19530"
        )
        schema = self.client.create_schema(
            #     auto_id=True,
            enable_dynamic_field=True,
        )
        self.collection_name = 'plan_' + str(plan_id)

        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=768)
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="id",
            index_type="STL_SORT"
        )

        index_params.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128}
        )
        self.client.create_collection(
            self.collection_name,
            schema=schema,
            index_params=index_params
        )

        res = self.client.get_load_state(
            self.collection_name
        )
        try:
            insert_result = self.client.insert(
                self.collection_name,
                data=data
            )
            print("Insert result:", insert_result)
        except Exception as e:
            print(f"An error occurred: {e}")
        self.client.refresh_load(self.collection_name)

    def predict(self, events, keywords, titles, titles_id):
        """

        :param events: [[id,name],[id,name],...]
        :param keywords:
        :param titles: titles
        :param titles_id: titles_id
        :return:
        """
        self.client = MilvusClient(
            uri="http://10.63.146.221:19530"
        )
        event_name2id_dict = {}
        event_result_id = {}
        event_result_title = {}
        for event_id, event_name in events:
            event_result_id[event_name] = []
            event_result_title[event_name] = []

            event_name2id_dict[event_name] = event_id
            if event_name == "非事件信息":
                event_name2id_dict["其他"] = event_id
        for event_id, event_name in events[:-1]:
            d = keywords + [event_name]
            search_embeddings = self.bce_emb_model.encode(d)
            search_params = {"metric_type": "COSINE", "params": {}}
            results = self.client.search(self.collection_name, search_embeddings, search_params=search_params,
                                         limit=500,
                                         output_fields=["id", "title"])
            remain_titles = set()
            for i in results:
                for j in i:
                    if j['distance'] > 0.3:
                        remain_titles.add((j['entity']["id"], j['entity']['title']))
            remain_titles = list(remain_titles)
            if len(remain_titles) == 0:
                continue
            sentence_pairs = [(event_name, i[1]) for i in remain_titles]

            pairs_scores = self.bce_reranker_model.compute_score(sentence_pairs)
            score_th = max(pairs_scores) * 0.9
            for idx, score in enumerate(pairs_scores):
                if score >= score_th:
                    event_result_id[event_name].append(remain_titles[idx][0])
                    event_result_title[event_name].append(remain_titles[idx][1])
        # print(event_result_id, event_result_title)
        classifier = pipeline('zero-shot-classification',
                              '/mnt/data/users/xhd/tsgz/model_dir/nlp_structbert_zero-shot-classification_chinese-large',
                              device="cuda:1")
        labels = [i[1] for i in events[:-1]]
        labels.append("其他")
        print(labels)
        results = classifier(titles, candidate_labels=labels)
        print(results)
        for t, t_id, res in zip(titles, titles_id, results):
            label = res['labels'][0]
            score = res['scores'][0]
            if label == "其他":
                label = "非事件信息"
            if score > 0.45:

                if t not in event_result_title[label]:
                    event_result_id[label].append(t_id)
                    event_result_title[label].append(t)
        print('*' * 30)
        print(event_result_title)
        merged_list = list(chain.from_iterable(event_result_id.values()))
        id_not_in_final_result = []
        title_not_in_final_result = []
        for i, j in zip(titles_id, titles):
            if i not in merged_list:
                id_not_in_final_result.append(i)
                title_not_in_final_result.append(j)

        news_by_event = {}  # {"event_id":[news_id, news_id, ...]}
        titles_by_event = {}
        for e_id, t_ids in event_result_id.items():
            news_by_event[event_name2id_dict[e_id]] = t_ids
        news_by_event[event_name2id_dict["其他"]].extend(id_not_in_final_result)
        for e_id, t in event_result_title.items():
            titles_by_event[event_name2id_dict[e_id]] = t
        titles_by_event[event_name2id_dict["其他"]].extend(title_not_in_final_result)
        # print(final_result)
        return news_by_event, titles_by_event

    def close(self):
        self.client.drop_collection(self.collection_name)
        self.client.close()


if __name__ == '__main__':
    EC = EventCls()
    schema = ["美国大选投票统计", "遭遇枪击", "政策主张", "世界羽坛"]
    # EC.load(schema)
    # result = EC.predict(["特朗普，被枪击后被护送下台 - 照片捕捉到的事件的样子", "aaaa"])
    # print(result)
    data = [{"id": 123123, "title": "你好", "content": "中国"}, {"id": 33123, "title": "你好", "content": "中国"},
            {"id": 53123, "title": "你好", "content": "中国"}, {"id": 43123, "title": "你好", "content": "中国"}]
    EC.insert_milvus("12345", data)
