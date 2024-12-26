# -*- encoding: utf-8 -*-
# @ModuleName: EventCls
# @Author: ximo
# @Time: 2024/5/14 14:53


from BCEmbedding import EmbeddingModel, RerankerModel
from modelscope import pipeline
from pymilvus import MilvusClient, DataType

import config
import os


class EventCls():
    def __init__(self, batch_size=200):
        self.bs = batch_size
        self.client = None
        self.collection_name = None
        self.bce_emb_model = EmbeddingModel(model_name_or_path=config.MODEL_CONFIG["bce-embedding-base_v1"],
                                            device="cuda:0")
        self.bce_reranker_model = RerankerModel(model_name_or_path=config.MODEL_CONFIG["bce-reranker-base_v1"],
                                                device="cuda:0")

        self.classifier = pipeline('zero-shot-classification',
                                   config.MODEL_CONFIG["nlp_structbert_zero-shot-classification_chinese-large"],
                                   device="cuda:0")

    def insert_milvus(self, plan_id, data, is_news=True, ):
        """

        :param plan_id:
        :param data: [{}]
        :param is_news: 是否为新闻
        :return:
        """
        if is_news:
            data_ = [i["title"] + i["content"] for i in data]
            self.collection_name = 'plan_' + str(plan_id) + "_news"
        else:
            data_ = [i["title"][:500] for i in data]
            self.collection_name = 'plan_' + str(plan_id) + "_post"
        data_t = [i if i is not None and i != "" else " " for i in data_]
        data_emb = self.bce_emb_model.encode(data_t, enable_tqdm=False, batch_size=self.bs).tolist()
        for idx, i in enumerate(data):
            i["embedding"] = data_emb[idx]
        mode = os.environ['tsgz_mode']
        if mode == 'test':
            config_module = 'config'
        else:
            config_module = 'config_pro'

        config = __import__(config_module)

        Milvus_config = config.MILVUS_CONFIG
        # self.client = MilvusClient(
        #     uri="http://10.63.146.221:19530",
        # )
        self.client = MilvusClient(
            **Milvus_config
        )
        schema = self.client.create_schema(
            #     auto_id=True,
            enable_dynamic_field=True,
        )

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
            batch_size = 1000
            total_data = len(data)

            # 对数据进行切片，批量插入
            for i in range(0, total_data, batch_size):
                batch = data[i:i + batch_size]
                self.client.insert(self.collection_name, data=batch)
            # insert_result = self.client.insert(
            #     self.collection_name,
            #     data=data
            # )
            # print("Insert result:", insert_result)
        except Exception as e:
            print(f"An error occurred: {e}")
        self.client.refresh_load(self.collection_name)
        return data_emb

    def predict(self, events, keywords, titles, titles_id):
        """

        :param events: [[id,name],[id,name],...]
        :param keywords:
        :param titles: titles
        :param titles_id: titles_id
        :return:
        """
        # self.client = MilvusClient(
        #     uri="http://10.63.146.221:19530"
        # )
        print(keywords)
        event_name2id_dict = {}
        event_result_id = {} # event 按id分
        event_result_title = {} # event按事件标题分
        for event_id, event_name in events:
            event_result_id[event_name] = []
            event_result_title[event_name] = []

            event_name2id_dict[event_name] = event_id
            if event_name == "非事件信息":
                event_name2id_dict["其他"] = event_id
        # labels = []
        # event_label_name_map = {'非事件信息': '非事件信息'}
        # for i in events[:-1]:
        #     label_temp = i[1]
        #     for j in keywords:
        #         label_temp = label_temp.replace(j, "")
        #     labels.append(label_temp)
        #     if label_temp in event_label_name_map:
        #         label_temp = i[1]
        #     event_label_name_map[label_temp] = i[1]
        labels = [i[1] for i in events[:-1]]
        # labels.append("其他")
        print(labels)
        # 零样本分类
        results = self.classifier(titles, candidate_labels=labels, multi_label=True)
        for t, t_id, res in zip(titles, titles_id, results):
            label = res['labels'][0]
            score = res['scores'][0]
            if label == "其他":
                label = "非事件信息"
            if score > 0.75:
                # label_event_name = event_label_name_map[label]
                label_event_name = label
                event_result_id[label_event_name].append(t_id)
                event_result_title[label_event_name].append(t)
            else:
                event_result_id["非事件信息"].append(t_id)
                event_result_title["非事件信息"].append(t)
        print(event_result_title)
        # 遍历每个事件，到Milvus中搜索
        for event_id, event_name in events[:-1]:
            # d = keywords + [event_name]
            # label_temp = event_name
            # for j in keywords:
            #     label_temp = label_temp.replace(j, "")
            # d = [label_temp]
            d = [event_name]
            # print(d)
            # 把keyword 去掉
            search_embeddings = self.bce_emb_model.encode(d, enable_tqdm=False, batch_size=self.bs)
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

            pairs_scores = self.bce_reranker_model.compute_score(sentence_pairs, enable_tqdm=False)
            if not isinstance(pairs_scores, list):
                pairs_scores = [pairs_scores]
            score_th = max(pairs_scores) * 0.9
            for idx, score in enumerate(pairs_scores):
                if score >= score_th and remain_titles[idx][0] not in event_result_id["非事件信息"] and \
                        remain_titles[idx][0] not in event_result_id[event_name]:
                    event_result_id[event_name].append(remain_titles[idx][0])
                    event_result_title[event_name].append(remain_titles[idx][1])
        # 整合零样本和Milvus的结果
        news_by_event = {}  # {"event_id":[news_id, news_id, ...]}
        titles_by_event = {}
        # event_name to event_id
        for e_name, t_ids in event_result_id.items():
            news_by_event[event_name2id_dict[e_name]] = t_ids
        for e_name, t in event_result_title.items():
            titles_by_event[event_name2id_dict[e_name]] = t
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
