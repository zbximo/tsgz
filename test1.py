# # -*- encoding: utf-8 -*-
# # @ModuleName: test1
# # @Author: ximo
# # @Time: 2024/8/12 17:54
# from modelscope.pipelines import pipeline
# from pymilvus import MilvusClient, DataType
# import time
# from BCEmbedding import EmbeddingModel,RerankerModel
# bce_emb_model = EmbeddingModel(model_name_or_path="/mnt/data/users/xhd/tsgz/model_dir/bce-embedding-base_v1",
#                                             device="cpu")
# bce_reranker_model = RerankerModel(model_name_or_path="/mnt/data/users/xhd/tsgz/model_dir/bce-reranker-base_v1",
#                                         device="cpu")
# event_name = "特朗普与拜登选情分析"
# d = ['美国', '选举', '总统', '特朗普', '拜登', '投票', '枪击', '暗杀', '刺杀', '大选', '候选人', '特朗普与拜登选情分析']
# search_embeddings = bce_emb_model.encode(d)
# collection_name = "plan_164"
# search_params = {"metric_type": "COSINE", "params": {}}
# client = MilvusClient(
#     uri="http://10.63.146.221:19530"
# )
# results = client.search(collection_name, search_embeddings, search_params=search_params, limit=20, output_fields=["id","title"])
# remain_titles = set()
# print(results)
# for i in results:
#     for j in i:
#         if j['distance'] > 0.3:
#             remain_titles.add((j['entity']["id"],j['entity']['title']))
# #     rerank_results = bec_reranker_model.rerank(query=event_name, passages=titles)
# sentence_pairs = [(event_name, i[1]) for i in remain_titles]
# #     print(sentence_pairs)
# pairs_scores = bce_reranker_model.compute_score(sentence_pairs)
# score_th = max(pairs_scores) * 0.9
# print(sentence_pairs,pairs_scores)
# event_result = {
#     event_name:[]
# }
# for idx, score in enumerate(pairs_scores):
#     if score >= score_th:
#         event_result[event_name].append(sentence_pairs[idx][1])
# print('*'*30)
# print(event_result)


# *********************************************************************************************************

# from models.SentimentCls import SentimentCls
from paddlenlp import Taskflow
#
# import logging
# import time
# logging.error("111")

from services_pro.TaskService import TaskService
import os
os.environ['tsgz_mode'] = "test"
TS = TaskService('test')
TS.run_all_time_v2()
