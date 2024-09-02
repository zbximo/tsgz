# -*- encoding: utf-8 -*-
# @ModuleName: TaskService
# @Author: ximo
# @Time: 2024/5/9 11:04
import copy
import re
import time
from tqdm import tqdm

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


class TaskService():
    def __init__(self, mode='pro'):
        self.db = dbTools(mode)
        self.db.open()
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def analyze_task_v2(self):

        session = self.db.get_new_session()
        # get tasks
        task_query = session.query(DataTask).filter(and_(DataTask.status == 0)).order_by(DataTask.create_date.asc())
        task_result = task_query.all()

        # print(f'{task_result=}')
        self.log_pro.info(len(task_result))
        if len(task_result) == 0:
            session.close()
            return 0
        EC = EventCls()

        cluster = Cluster()
        cluster.load_text_emb(device='cuda:0')
        # cluster.load_pos_model()
        snowflake = SnowFlake()
        for task in task_result:
            self.log_pro.info(f'{task.id=} start')
            del_session = self.db.get_new_session()
            del_session.query(DataAdd).filter(DataAdd.task_id == task.id).delete()
            del_session.commit()
            del_session.close()
            task: DataTask
            post_id_list = eval(task.post_id_list) if task.post_id_list else None
            new_id_list = eval(task.news_id_list) if task.news_id_list else None
            print(f'{len(post_id_list)=}', f'{len(new_id_list)=}')

            if new_id_list is not None and len(new_id_list) != 0:
                news_query: Query = session.query(DataNew).filter(DataNew.id.in_(new_id_list))
                news_list = news_query.all()
                news_zh_titles = [j.title if j.title is not None and j.title != "" else " " for j in news_list]
                e_session = self.db.get_new_session()

                events = e_session.query(DataEvent).filter(
                    DataEvent.plan_id == task.plan_id).order_by(
                    case(
                        [(DataEvent.title == '非事件信息', 1)],
                        else_=0
                    ).asc(),
                ).all()
                event_titles = [j.title for j in events]
                not_event_id = events[-1].id
                # v1 计算事件与新闻的相似度，排除非事件信息
                # max_indexs, max_score = cluster.similarity(news_zh_titles, event_titles[:-1], 0.5)
                # v2 zero_shot
                schema = event_titles[:-1]
                schema.append("其他")
                EC.load(schema)
                max_indexs, max_score = EC.predict(news_zh_titles)

                data_by_event = {}  # {"event_id":[news_id, news_id, ...]}
                titles_data_by_event = {}
                # ori_data_by_event = {}
                # 遍历添加data_add表
                add_session = self.db.get_new_session()
                for i, idx in enumerate(max_indexs):
                    dataAddid = snowflake.generate()
                    dataAdd = DataAdd()
                    dataAdd.id = dataAddid
                    dataAdd.task_id = task.id
                    dataAdd.plan_id = task.plan_id
                    dataAdd.newsId = news_list[i].id
                    dataAdd.event_id = events[idx].id
                    add_session.add(dataAdd)
                    add_session.commit()

                    # 按event_id添加到data_by_event
                    if events[idx].id not in data_by_event:
                        data_by_event[events[idx].id] = [news_list[i].id]
                        titles_data_by_event[events[idx].id] = [news_list[i].title]
                    else:
                        data_by_event[events[idx].id].append(news_list[i].id)
                        titles_data_by_event[events[idx].id].append(news_list[i].title)
                add_session.close()
                e_session.close()
                for k, v in data_by_event.items():
                    self.log_pro.info(f'event id:{k}, news: {len(v)}')
                # 添加data_event表
                q_session = self.db.get_new_session()
                for k, v in data_by_event.items():
                    event: DataEvent = q_session.query(DataEvent).filter(DataEvent.id == k).first()
                    if event.newsIds is None:
                        newsIds = v
                    else:
                        newsIds = eval(event.newsIds)
                        newsIds.extend(v)
                    newsIds = list(set(newsIds))
                    event.newsIds = str(newsIds)
                q_session.commit()
                q_session.close()
                # 相似新闻
                """
                1. 按event_id查询
                3. 遍历data_by_event[event_id]
                4. 计算相似度
                """

                for k, v in data_by_event.items():
                    q_session = self.db.get_new_session()
                    DataSimilars = q_session.query(DataSimilar).filter(DataSimilar.event_id == k).all()
                    DataSimilarsIds = [i.id for i in DataSimilars]
                    DataSimilarsNewsIds = [eval(i.news_ids) for i in DataSimilars]
                    DataSimilars_cnt = len(DataSimilars)
                    q_session.close()
                    if len(v)==0:
                        continue
                    if DataSimilars_cnt == 0:
                        cluster_news_result = cluster.cluster_sentences(titles_data_by_event[k], threshold=0.3) \
                            if len(v) > 1 else {0: [0]}
                        for ck, cv in cluster_news_result.items():
                            dataSimilar = DataSimilar()
                            dataSimilar.id = snowflake.generate()
                            dataSimilar.plan_id = task.plan_id
                            dataSimilar.news_ids = str([v[cindex] for cindex in cv])
                            dataSimilar.event_id = k
                            ds_session = self.db.get_new_session()
                            ds_session.add(dataSimilar)
                            ds_session.commit()
                            ds_session.close()
                    else:
                        threshold = 0.8
                        # 遍历event里面的每个新闻

                        # fast:v2
                        dsnewsids = [d[0] for d in DataSimilarsNewsIds]
                        q_session = self.db.get_new_session()
                        similar_news = q_session.query(DataNew.title).filter(
                            DataNew.id.in_(dsnewsids)).all()
                        similar_news_list = [title[0] for title in similar_news]
                        q_session.close()
                        if k == not_event_id:
                            for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):

                                if i in similar_news_list:
                                    similar_dsid = dsnewsids[similar_news_list.index(i)]
                                    ds_session = self.db.get_new_session()
                                    ds = ds_session.query(DataSimilar).filter(DataSimilar.id == similar_dsid).first()
                                    newsIds = eval(ds.news_ids)
                                    newsIds.append(i)
                                    newsIds = list(set(newsIds))
                                    ds.news_ids = str(newsIds)
                                    ds_session.commit()
                                    ds_session.close()

                                else:
                                    dataSimilar = DataSimilar()
                                    rid = snowflake.generate()
                                    dataSimilar.id = rid
                                    dataSimilar.plan_id = task.plan_id
                                    dataSimilar.news_ids = str([i])
                                    dataSimilar.event_id = k
                                    ds_session = self.db.get_new_session()
                                    ds_session.add(dataSimilar)
                                    ds_session.commit()
                                    ds_session.close()
                                    DataSimilarsIds.append(rid)
                                    DataSimilarsNewsIds.append([i])
                                    dsnewsids.append(i)
                                    similar_news_list.append(t)
                        else:
                            for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):
                                similar_matrix, score = cluster.similarity(t, similar_news_list,
                                                                           threshold=threshold, use_emd=True)
                                if similar_matrix[0] < len(similar_news_list):
                                    max_similar_dsid = DataSimilarsIds[similar_matrix[0]]
                                    ds_session = self.db.get_new_session()
                                    ds = ds_session.query(DataSimilar).filter(
                                        DataSimilar.id == max_similar_dsid).first()
                                    newsIds = eval(ds.news_ids)
                                    newsIds.append(i)
                                    newsIds = list(set(newsIds))
                                    ds.news_ids = str(newsIds)
                                    ds_session.commit()
                                    ds_session.close()

                                else:
                                    dataSimilar = DataSimilar()
                                    rid = snowflake.generate()
                                    dataSimilar.id = rid
                                    dataSimilar.plan_id = task.plan_id
                                    dataSimilar.news_ids = str([i])
                                    dataSimilar.event_id = k
                                    ds_session = self.db.get_new_session()
                                    ds_session.add(dataSimilar)
                                    ds_session.commit()
                                    ds_session.close()

                                    DataSimilarsIds.append(rid)
                                    DataSimilarsNewsIds.append([i])
                                    dsnewsids.append(i)
                                    similar_news_list.append(t)

            if post_id_list is not None and len(post_id_list) != 0:
                posts_query: Query = session.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list))
                posts_list = posts_query.all()
                posts_zh_titles = [j.title if j.title  is not None and j.title != "" else " " for j in posts_list]
                e_session = self.db.get_new_session()

                events = e_session.query(DataEvent).filter(
                    DataEvent.plan_id == task.plan_id).order_by(
                    case(
                        [(DataEvent.title == '非事件信息', 1)],
                        else_=0
                    ).asc(),
                ).all()
                event_titles = [j.title for j in events]

                # zero_shot
                schema = event_titles[:-1]
                schema.append("其他")
                EC.load(schema)
                max_indexs, max_score = EC.predict(posts_zh_titles)

                data_by_event = {}  # {"event_id":[news_id, news_id, ...]}
                titles_data_by_event = {}
                # ori_data_by_event = {}
                # 遍历添加data_add表
                add_session = self.db.get_new_session()
                for i, idx in enumerate(max_indexs):
                    dataAddid = snowflake.generate()
                    dataAdd = DataAdd()
                    dataAdd.id = dataAddid
                    dataAdd.task_id = task.id
                    dataAdd.plan_id = task.plan_id
                    dataAdd.postId = posts_list[i].id
                    dataAdd.event_id = events[idx].id
                    add_session.add(dataAdd)
                    add_session.commit()

                    # 按event_id添加到data_by_event
                    if events[idx].id not in data_by_event:
                        data_by_event[events[idx].id] = [posts_list[i].id]
                        titles_data_by_event[events[idx].id] = [posts_list[i].title]
                    else:
                        data_by_event[events[idx].id].append(posts_list[i].id)
                        titles_data_by_event[events[idx].id].append(posts_list[i].title)
                add_session.close()
                e_session.close()
                for k, v in data_by_event.items():
                    self.log_pro.info(f'event id:{k}, posts: {len(v)}')
                # 添加data_event表
                q_session = self.db.get_new_session()
                for k, v in data_by_event.items():
                    event: DataEvent = q_session.query(DataEvent).filter(DataEvent.id == k).first()
                    if event.postIds is None:
                        postIds = v
                    else:
                        postIds = eval(event.postIds)
                        postIds.extend(v)
                    postIds = list(set(postIds))
                    event.postIds = str(postIds)
                q_session.commit()
                q_session.close()

            task.status = 1

            # print(task.__dict__)
            self.log_pro.info(f'{task.id=} over')
            session.commit()

        session.close()

        return 1

    def run_all_time_v2(self):
        while True:
            r = self.analyze_task_v2()
            if r == 0:
                time.sleep(60)


if __name__ == '__main__':
    TS = TaskService()
    TS.run_all_time_v2()
