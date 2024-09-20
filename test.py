# # # -*- encoding: utf-8 -*-
# # # @ModuleName: test
# # # @Author: ximo
# # # @Time: 2024/5/20 15:12
# #
# # import argparse
# #
# # from services.TaskService import TaskService
# #
# #
# # def main():
# #     # 创建 ArgumentParser 对象
# #     parser = argparse.ArgumentParser(description='Script description')
# #
# #     # 添加参数 method_id
# #     parser.add_argument('--method_id', type=int, help='Method ID')
# #
# #     # 添加参数 plan_id
# #     parser.add_argument('--plan_id', type=int, help='Plan ID')
# #
# #     # 解析命令行参数
# #     args = parser.parse_args()
# #
# #     method_id = args.method_id
# #     plan_id = args.plan_id
# #     print(f'{method_id=},{plan_id=}')
# #     if method_id is not None and plan_id is not None:
# #         ts = TaskService()
# #         ts.analyze_task(id=method_id, plan_id=plan_id)
# #
# #
# # if __name__ == '__main__':
# #     main()
# import time
#
# from models.EventCls import EventCls
# from utils.Tools import *
# from sqlalchemy.orm import Query
# from sqlalchemy import func, or_, and_, desc, case
# from collections import Counter
#
# from db.database import dbTools
# from db.entity import *
# from models.Cluster import *
# import jieba
# import log_pro
# import os
# import pandas as pd
# from tqdm import tqdm
# # mode = 'test'
# # db = dbTools(mode)
# # db.open(use_ssh=True)
# # q_session = db.get_new_session()
# # new = q_session.query(DataEvent).filter(and_(DataEvent.prediction == None, DataEvent.title != "非事件信息")).all()
# # for i in new:
# #     print(i.__dict__)
# # q_session.close()
#
# # news = q_session.query(DataNew).filter(DataNew.id.in_([2, 3, 4])).all()
# #
# # for i in news:
# #     print(111,i.__dict__)
# #     i.title = str(i.title)[:-1]
# #     q_session.commit()
# #     print(112,i.__dict__)
# # time.sleep(10)
# # for i in news:
# #     print(211,i.__dict__)
# #     i.title = str(i.title)[:-1]
# #     q_session.commit()
# #     print(222,i.__dict__)
# # q_session.close()
# # q_session.commit()
#
# # cluster = Cluster()
# # cluster.load_text_emb()
# # cluster.get_embedding(["我的你的好的"]*100).tolist()
#
#
# # from services_pro.TaskService import TaskService
# # from services_pro.NewsService import NewsService
# # from services_pro.SocialPostService import SocialPostService
# # import time
# # #
# # # #
# # os.environ["tsgz_mode"] = "test_v2"
# # ts = TaskService("test", use_ssh=True)
# # while True:
# #     ts.analyze_task_v2()
# #     time.sleep(60)
#
#
# # from  utils import Tools
# # Tools.db2model()
# from utils.Tools import *
#
# mode = 'test'
# db = dbTools(mode)
# db.open()
# session = db.get_new_session()
# # get tasks
# task_query = session.query(DataTask).filter(DataTask.id == 1819040831813861378)
# task_result = task_query.all()
#
# cluster = Cluster()
# cluster.load_text_emb(device='cuda:1')
# # cluster.load_pos_model()
# snowflake = SnowFlake()
# for task in task_result:
#     EC = EventCls()
#     del_session = db.get_new_session()
#     del_session.query(DataAdd).filter(DataAdd.task_id == task.id).delete()
#     del_session.commit()
#     del_session.close()
#     task: DataTask
#     post_id_list = eval(task.post_id_list) if task.post_id_list else None
#     new_id_list = eval(task.news_id_list) if task.news_id_list else None
#     print(f'{len(post_id_list)=}', f'{len(new_id_list)=}')
#
#     if new_id_list is not None and len(new_id_list) != 0:
#         news_query: Query = session.query(DataNew).filter(DataNew.id.in_(new_id_list))
#         news_list = news_query.all()
#         insert_data = [{"id": i.id, "title": i.title, "content": i.content} for i in news_list]
#         news_zh_titles = [j.title for j in news_list]
#         news_id = [j.id for j in news_list]
#         e_session = db.get_new_session()
#
#         events = e_session.query(DataEvent).filter(
#             DataEvent.plan_id == task.plan_id).order_by(
#             case(
#                 [(DataEvent.title == '非事件信息', 1)],
#                 else_=0
#             ).asc(),
#         ).all()
#
#         event_id_titles = [[j.id, j.title] for j in events]
#         EC.insert_milvus(task.plan_id, insert_data)
#         data_by_event, titles_data_by_event = EC.predict(event_id_titles, task.keywords.split(","),
#                                                          news_zh_titles, news_id)
#         # ori_data_by_event = {}
#         # 遍历添加data_add表
#         add_session = db.get_new_session()
#         for e_id, new_ids in data_by_event.items():
#             for nid in new_ids:
#                 dataAddid = snowflake.generate()
#                 dataAdd = DataAdd()
#                 dataAdd.id = dataAddid
#                 dataAdd.task_id = task.id
#                 dataAdd.plan_id = task.plan_id
#                 dataAdd.newsId = nid
#                 dataAdd.event_id = e_id
#                 add_session.add(dataAdd)
#                 add_session.commit()
#
#         add_session.close()
#         e_session.close()
#         EC.close()
#         del EC
#         # 添加data_event表
#         q_session = db.get_new_session()
#         for k, v in data_by_event.items():
#             event: DataEvent = q_session.query(DataEvent).filter(DataEvent.id == k).first()
#             if event.newsIds is None:
#                 newsIds = v
#             else:
#                 newsIds = eval(event.newsIds)
#                 newsIds.extend(v)
#             newsIds = list(set(newsIds))
#             event.newsIds = str(newsIds)
#         q_session.commit()
#         q_session.close()
#         # 相似新闻
#         """
#         1. 按event_id查询
#         3. 遍历data_by_event[event_id]
#         4. 计算相似度
#         """
#         q_session = db.get_new_session()
#         print(f'{data_by_event=}')
#         print(f'{titles_data_by_event=}')
#         for k, v in data_by_event.items():
#             DataSimilars = q_session.query(DataSimilar).filter(DataSimilar.event_id == k).all()
#             DataSimilarsIds = [i.id for i in DataSimilars]
#             DataSimilarsNewsIds = [eval(i.news_ids) for i in DataSimilars]
#             if len(DataSimilars) == 0:
#                 cluster_news_result = cluster.cluster_sentences(titles_data_by_event[k], threshold=0.3) \
#                     if len(v) > 1 else {0: [0]}
#                 for ck, cv in cluster_news_result.items():
#                     dataSimilar = DataSimilar()
#                     dataSimilar.id = snowflake.generate()
#                     dataSimilar.plan_id = task.plan_id
#                     dataSimilar.news_ids = str([v[cindex] for cindex in cv])
#                     dataSimilar.event_id = k
#                     q_session.add(dataSimilar)
#             else:
#                 threshold = 0.8
#                 # fast:v2
#                 dsnewsids = [d[0] for d in DataSimilarsNewsIds]
#                 similar_news = q_session.query(DataNew.title).filter(
#                     DataNew.id.in_(dsnewsids)).all()
#                 similar_news_list = [title[0] for title in similar_news]
#                 print(1, time.time())
#                 for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):
#                     print(1.2,len(similar_news_list))
#                     similar_matrix, score = cluster.similarity(t, similar_news_list,
#                                                                threshold=threshold, use_emd=True)
#                     print(2, time.time())
#                     # dsnewsids = [d[0] for d in DataSimilarsNewsIds]
#                     # similar_news = q_session.query(DataNew.title).filter(
#                     #     DataNew.id.in_(dsnewsids)).all()
#                     # similar_news_list = [title[0] for title in similar_news]
#                     if similar_matrix[0] < len(similar_news_list):
#                         max_similar_dsid = DataSimilarsIds[similar_matrix[0]]
#                         for ds in DataSimilars:
#                             if ds.id == max_similar_dsid:
#                                 newsIds = eval(ds.news_ids)
#                                 newsIds.append(i)
#                                 newsIds = list(set(newsIds))
#                                 ds.news_ids = str(newsIds)
#                     else:
#                         dataSimilar = DataSimilar()
#                         rid = snowflake.generate()
#                         dataSimilar.id = rid
#                         dataSimilar.plan_id = task.plan_id
#                         dataSimilar.news_ids = str([i])
#                         dataSimilar.event_id = k
#                         q_session.add(dataSimilar)
#                         DataSimilarsIds.append(rid)
#                         DataSimilarsNewsIds.append([i])
#                         dsnewsids.append(i)
#                         similar_news_list.append(t)
#
#             q_session.commit()
#         q_session.close()
#     EC = EventCls()
#     if post_id_list is not None and len(post_id_list) != 0:
#         posts_query: Query = session.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list))
#         posts_list = posts_query.all()
#         insert_data = [{"id": i.id, "title": i.title} for i in posts_list]
#         post_zh_titles = [j.title for j in posts_list]
#         post_id = [j.id for j in posts_list]
#         e_session = db.get_new_session()
#
#         events = e_session.query(DataEvent).filter(
#             DataEvent.plan_id == task.plan_id).order_by(
#             case(
#                 [(DataEvent.title == '非事件信息', 1)],
#                 else_=0
#             ).asc(),
#         ).all()
#
#         event_id_titles = [[j.id, j.title] for j in events]
#         EC.insert_milvus(task.plan_id, insert_data)
#         data_by_event, titles_data_by_event = EC.predict(event_id_titles, task.keywords.split(","),
#                                                          post_zh_titles, post_id)
#         # ori_data_by_event = {}
#         # 遍历添加data_add表
#         add_session = db.get_new_session()
#         for e_id, p_ids in data_by_event.items():
#             for pid in p_ids:
#                 dataAddid = snowflake.generate()
#                 dataAdd = DataAdd()
#                 dataAdd.id = dataAddid
#                 dataAdd.task_id = task.id
#                 dataAdd.plan_id = task.plan_id
#                 dataAdd.postId = pid
#                 dataAdd.event_id = e_id
#                 add_session.add(dataAdd)
#                 add_session.commit()
#
#         add_session.close()
#         e_session.close()
#         EC.close()
#         del EC
#         # 添加data_event表
#         q_session = db.get_new_session()
#         for k, v in data_by_event.items():
#             event: DataEvent = q_session.query(DataEvent).filter(DataEvent.id == k).first()
#             if event.postIds is None:
#                 postIds = v
#             else:
#                 postIds = eval(event.postIds)
#                 postIds.extend(v)
#             postIds = list(set(postIds))
#             event.postIds = str(postIds)
#         q_session.commit()
#         q_session.close()
#
#     # task.status = 1
#
#     print(task.__dict__)
#     session.close()
from sqlalchemy import and_

from db.database import dbTools
from db.entity import DataTask

# db = dbTools("test")
# db.open()
# session = db.get_new_session()
# task_ids = ["1826137278634455041"]
# task_query = session.query(DataTask).filter(and_( DataTask.id.in_(task_ids))).order_by(DataTask.create_date.asc())
# for i in task_query:
#     print(i.__dict__)
# session.close()
# x = {
#     'task_i1d': 1
# }
# try:
#     task_id_ = x.get('task_id',None)
#     x = 1 / 0
# except Exception as e:
#     print(f'{task_id_=},')
from services_pro.TaskService import TaskService
from services_pro.NewsService import NewsService
from services_pro.SocialPostService import SocialPostService
import os
os.environ['tsgz_mode'] = "test"
# TS = TaskService('test')
# TS.run_all_time_v2()
# ns = NewsService('test')
# ns.run_all_time()
sps = SocialPostService('test')
sps.run_all_time()