# # -*- encoding: utf-8 -*-
# # @ModuleName: test
# # @Author: ximo
# # @Time: 2024/5/20 15:12
#
# import argparse
#
# from services.TaskService import TaskService
#
#
# def main():
#     # 创建 ArgumentParser 对象
#     parser = argparse.ArgumentParser(description='Script description')
#
#     # 添加参数 method_id
#     parser.add_argument('--method_id', type=int, help='Method ID')
#
#     # 添加参数 plan_id
#     parser.add_argument('--plan_id', type=int, help='Plan ID')
#
#     # 解析命令行参数
#     args = parser.parse_args()
#
#     method_id = args.method_id
#     plan_id = args.plan_id
#     print(f'{method_id=},{plan_id=}')
#     if method_id is not None and plan_id is not None:
#         ts = TaskService()
#         ts.analyze_task(id=method_id, plan_id=plan_id)
#
#
# if __name__ == '__main__':
#     main()
from models.EventCls import EventCls
from utils.Tools import *
from sqlalchemy.orm import Query
from sqlalchemy import func, or_, and_, desc, case
from collections import Counter

from db.database import dbTools
from db.entity import *
from models.Cluster import *
import jieba
import log_pro
import os

# mode = 'test'
# db = dbTools(mode)
# db.open(use_ssh=True)
# q_session = db.get_new_session()
# new = q_session.query(DataEvent).filter(and_(DataEvent.prediction == None, DataEvent.title != "非事件信息")).all()
# for i in new:
#     print(i.__dict__)
# q_session.close()

# news = q_session.query(DataNew).filter(DataNew.id.in_([2, 3, 4])).all()
#
# for i in news:
#     print(111,i.__dict__)
#     i.title = str(i.title)[:-1]
#     q_session.commit()
#     print(112,i.__dict__)
# time.sleep(10)
# for i in news:
#     print(211,i.__dict__)
#     i.title = str(i.title)[:-1]
#     q_session.commit()
#     print(222,i.__dict__)
# q_session.close()
# q_session.commit()

# cluster = Cluster()
# cluster.load_text_emb()
# cluster.get_embedding(["我的你的好的"]*100).tolist()


# from services_pro.TaskService import TaskService
# from services_pro.NewsService import NewsService
# from services_pro.SocialPostService import SocialPostService
# import time
# #
# # #
# os.environ["tsgz_mode"] = "test_v2"
# ts = TaskService("test", use_ssh=True)
# while True:
#     ts.analyze_task_v2()
#     time.sleep(60)


# from  utils import Tools
# Tools.db2model()

mode = 'test'
db = dbTools(mode)
db.open(use_ssh=False)
session = db.get_new_session()
# get tasks
task_query = session.query(DataTask).filter(DataTask.id == 1813151490638012417)
task_result = task_query.all()
stop_words = get_stopwords()
EC = EventCls()

cluster = Cluster()
cluster.load_text_emb(device='cuda:0')
# cluster.load_pos_model()
for task in task_result:
    task: DataTask
    post_id_list = eval(task.post_id_list) if task.post_id_list else None
    new_id_list = eval(task.news_id_list) if task.news_id_list else None
    print(f'{len(post_id_list)=}', f'{len(new_id_list)=}')
    news_query: Query = session.query(DataNew).filter(DataNew.id.in_(new_id_list))
    news_list = news_query.all()
    news_zh_titles = [j.title for j in news_list]

    events = session.query(DataEvent).filter(
        DataEvent.plan_id == task.plan_id).order_by(
        case(
            [(DataEvent.title == '非事件信息', 1)],
            else_=0
        ).asc(),
    ).all()
    event_titles = [j.title for j in events]
    # v1 计算事件与新闻的相似度，排除非事件信息
    # max_indexs, max_score = cluster.similarity(news_zh_titles, event_titles[:-1], 0.5)
    # v2 zero_shot
    schema = event_titles[:-1]
    schema.append("其他")
    EC = EventCls()
    EC.load(schema)
    max_indexs, max_score = EC.predict(news_zh_titles)

    data_by_event = {}  # {"event_id":[news_id, news_id, ...]}
    titles_data_by_event = {}
    # ori_data_by_event = {}
    # 遍历添加data_add表
    for i, idx in enumerate(max_indexs):
        dataAdd = DataAdd()
        dataAdd.task_id = task.id
        dataAdd.plan_id = task.plan_id
        dataAdd.newsId = news_list[i].id
        dataAdd.event_id = events[idx].id
        # print(dataAdd.__dict__)
        # 按event_id添加到data_by_event
        if events[idx].id not in data_by_event:
            data_by_event[events[idx].id] = [news_list[i].id]
            titles_data_by_event[events[idx].id] = [news_list[i].title]
        else:
            data_by_event[events[idx].id].append(news_list[i].id)
            titles_data_by_event[events[idx].id].append(news_list[i].title)
    print(data_by_event)
    print('*'*30)
    print(titles_data_by_event)
    for k,v in data_by_event.items():
        print(k,len(v))
