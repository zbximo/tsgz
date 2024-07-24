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
    def __init__(self, mode='pro', use_ssh=False):
        self.db = dbTools(mode)
        self.db.open(use_ssh=use_ssh)
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def analyze_task(self):
        session = self.db.get_new_session()

        task_query = session.query(DataTask).filter(and_(DataTask.status == 0))
        task_result = task_query.all()
        # print(f'{task_result=}')
        self.log_pro.info(len(task_result))

        if len(task_result) == 0:
            session.close()
            return 0
        # with open("../utils/baidu_stopwords.txt", "r") as f:
        #     stop_words = f.read().splitlines()
        stop_words = get_stopwords()
        cluster = Cluster()
        cluster.load_text_emb()
        cluster.load_pos_model()
        for task in task_result:
            self.log_pro.info(f'{task.id=} start')

            task: DataTask
            post_id_list = eval(task.post_id_list) if task.post_id_list else None
            new_id_list = eval(task.news_id_list) if task.news_id_list else None
            if len(new_id_list) == 0:
                task.status = 1
                self.log_pro.info(f'{task.id=} over')
                session.commit()
                continue
            # cluster and topic model for news
            news_query: Query = session.query(DataNew).filter(DataNew.id.in_(new_id_list))
            news = news_query.all()
            news_original_titles = [j.original_title for j in news]

            cluster_result = cluster.cluster_titles_agg(news_original_titles)

            snowflake = SnowFlake()
            for k, v in cluster_result.items():
                dataEvent = DataEvent()
                dataEventid = snowflake.generate()
                dataEvent.id = dataEventid
                dataEvent.plan_id = task.plan_id
                dataEvent.task_id = task.id
                news_ids = [news[index].id for index in v]
                news_titles = [news[index].title for index in v]
                news_ori_titles = [news[index].original_title for index in v]
                dataEvent.newsIds = str(news_ids)
                # 识别相似新闻
                cluster_news_result = cluster.cluster_sentences(news_ori_titles, threshold=0.3) \
                    if len(news_ori_titles) > 1 else {0: [0]}
                for ck, cv in cluster_news_result.items():
                    dataSimilar = DataSimilar()
                    dataSimilar.id = snowflake.generate()
                    dataSimilar.plan_id = task.plan_id
                    dataSimilar.news_ids = str([news_ids[cindex] for cindex in cv])
                    dataSimilar.event_id = dataEventid
                    session.add(dataSimilar)

                # 分词,统计词频
                data = "。".join(news_titles)
                seg_list = jieba.cut(data)
                words = [word for word in seg_list if word not in stop_words]
                words = [word for word in words if not word.isdigit()]
                words = [word for word in words if not re.fullmatch(r'[a-zA-Z]+', word)]

                word_counts = Counter(words)
                top_words = [word for word, count in word_counts.most_common(3)]
                filters = [DataSocialPost.title.contains(word) for word in top_words]
                # 在Posts中搜索关键词
                session_q = self.db.get_new_session()
                post_query = session_q.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list)) \
                    .filter(and_(*filters)).all()
                dataEvent.postIds = str([p.id for p in post_query])
                session_q.close()

                session.add(dataEvent)
            task.status = 1
            self.log_pro.info(f'{task.id=} over')
            session.commit()
        session.close()
        return 1

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

        # with open("../utils/baidu_stopwords.txt", "r") as f:
        #     stop_words = f.read().splitlines()
        stop_words = get_stopwords()
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
                news_zh_titles = [j.title for j in news_list]
                e_session = self.db.get_new_session()

                events = e_session.query(DataEvent).filter(
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
                q_session = self.db.get_new_session()

                for k, v in data_by_event.items():
                    DataSimilars = q_session.query(DataSimilar).filter(DataSimilar.event_id == k).all()
                    DataSimilarsIds = [i.id for i in DataSimilars]
                    DataSimilarsNewsIds = [eval(i.news_ids) for i in DataSimilars]
                    if len(DataSimilars) == 0:
                        cluster_news_result = cluster.cluster_sentences(titles_data_by_event[k], threshold=0.3) \
                            if len(v) > 1 else {0: [0]}
                        for ck, cv in cluster_news_result.items():
                            dataSimilar = DataSimilar()
                            dataSimilar.id = snowflake.generate()
                            dataSimilar.plan_id = task.plan_id
                            dataSimilar.news_ids = str([v[cindex] for cindex in cv])
                            dataSimilar.event_id = k
                            q_session.add(dataSimilar)
                    else:
                        threshold = 0.8
                        # 遍历event里面的每个新闻

                        # fast:v2
                        dsnewsids = [d[0] for d in DataSimilarsNewsIds]
                        similar_news = q_session.query(DataNew.title).filter(
                            DataNew.id.in_(dsnewsids)).all()
                        similar_news_list = [title[0] for title in similar_news]
                        for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):
                            similar_matrix, score = cluster.similarity(t, similar_news_list,
                                                                       threshold=threshold, use_emd=True)
                            # dsnewsids = [d[0] for d in DataSimilarsNewsIds]
                            # similar_news = q_session.query(DataNew.title).filter(
                            #     DataNew.id.in_(dsnewsids)).all()
                            # similar_news_list = [title[0] for title in similar_news]
                            if similar_matrix[0] < len(similar_news_list):
                                max_similar_dsid = DataSimilarsIds[similar_matrix[0]]
                                for ds in DataSimilars:
                                    if ds.id == max_similar_dsid:
                                        newsIds = eval(ds.news_ids)
                                        newsIds.append(i)
                                        newsIds = list(set(newsIds))
                                        ds.news_ids = str(newsIds)
                            else:
                                dataSimilar = DataSimilar()
                                rid = snowflake.generate()
                                dataSimilar.id = rid
                                dataSimilar.plan_id = task.plan_id
                                dataSimilar.news_ids = str([i])
                                dataSimilar.event_id = k
                                q_session.add(dataSimilar)
                                DataSimilarsIds.append(rid)
                                DataSimilarsNewsIds.append([i])
                                dsnewsids.append(i)  #
                                similar_news_list.append(t)  #
                        # # slow v1 遍历找最大值
                        # for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):
                        # max_similar_dsid = -1
                        # max_similar_score = threshold
                        # for ds_id, dsnewsids in zip(DataSimilarsIds, DataSimilarsNewsIds):
                        #     similar_news = q_session.query(DataNew.title).filter(
                        #         DataNew.id.in_(dsnewsids)).all()
                        #     similar_news_list = [title[0] for title in similar_news]
                        #
                        #     dsid = ds_id
                        #     similar_matrix, score = cluster.similarity(t, similar_news_list,
                        #                                                threshold=threshold, use_emd=True)
                        #     if max_similar_score < score[0]:
                        #         max_similar_score = score[0]
                        #         max_similar_dsid = dsid
                        #
                        # if max_similar_dsid != -1:
                        #     for ds in DataSimilars:
                        #         if ds.id == max_similar_dsid:
                        #             newsIds = eval(ds.news_ids)
                        #             newsIds.append(i)
                        #             newsIds = list(set(newsIds))
                        #             ds.news_ids = str(newsIds)
                        # else:
                        #     dataSimilar = DataSimilar()
                        #     rid = snowflake.generate()
                        #     dataSimilar.id = rid
                        #     dataSimilar.plan_id = task.plan_id
                        #     dataSimilar.news_ids = str([i])
                        #     dataSimilar.event_id = k
                        #     q_session.add(dataSimilar)
                        #     DataSimilarsIds.append(rid)
                        #     DataSimilarsNewsIds.append([i])

                    q_session.commit()
                q_session.close()

            if post_id_list is not None and len(post_id_list) != 0:
                events = session.query(DataEvent).filter(
                    DataEvent.plan_id == task.plan_id).order_by(
                    case(
                        [(DataEvent.title == '非事件信息', 1)],
                        else_=0
                    ).asc(),
                ).all()
                post_id_list_retain = copy.deepcopy(post_id_list)
                for e in events:
                    if e.title == "非事件信息":
                        session_a = self.db.get_new_session()
                        for p_id in post_id_list_retain:
                            dataAdd = DataAdd()
                            dataAdd.id = snowflake.generate()
                            dataAdd.task_id = task.id
                            dataAdd.plan_id = task.plan_id
                            dataAdd.postId = p_id
                            dataAdd.event_id = e.id
                            session_a.add(dataAdd)
                            session_a.commit()
                        session_a.close()
                        break
                    if e.newsIds is None:
                        continue

                    e_news = session.query(DataNew.title).filter(
                        DataNew.id.in_(eval(e.newsIds))).all()
                    e_news = [e_news_title[0] for e_news_title in e_news]
                    data = "。".join(e_news)
                    seg_list = jieba.cut(data)
                    words = [word for word in seg_list if word not in stop_words and len(word) > 1]
                    words = [word for word in words if not word.isdigit()]
                    words = [word for word in words if not re.fullmatch(r'[a-zA-Z]+', word)]

                    word_counts = Counter(words)
                    top_words = [word for word, count in word_counts.most_common(3)]
                    self.log_pro.info(f'{task.id=}, {top_words=}')

                    filters = [DataSocialPost.title.contains(word) for word in top_words]
                    session_p = self.db.get_new_session()
                    post_query = session_p.query(DataSocialPost.id).filter(DataSocialPost.id.in_(post_id_list)) \
                        .filter(and_(*filters)).all()
                    if len(post_query) == 0:
                        continue
                    add_postId_list = [p[0] for p in post_query]
                    session_a = self.db.get_new_session()

                    for add_post_id in add_postId_list:
                        try:
                            post_id_list_retain.remove(add_post_id)
                        except Exception:
                            pass
                        dataAdd = DataAdd()
                        dataAdd.id = snowflake.generate()
                        dataAdd.task_id = task.id
                        dataAdd.plan_id = task.plan_id
                        dataAdd.postId = add_post_id
                        dataAdd.event_id = e.id
                        session_a.add(dataAdd)
                        session_a.commit()
                    session_a.close()
                    postIds = eval(e.postIds)
                    postIds.extend(add_postId_list)
                    postIds = list(set(postIds))
                    e.postIds = str(postIds)
                    session_p.close()
                    session.commit()
            task.status = 1

            # print(task.__dict__)
            self.log_pro.info(f'{task.id=} over')
            session.commit()

        session.close()

        return 1

    def run_all_time(self):
        while True:
            r = self.analyze_task()
            if r == 0:
                time.sleep(60)

    def run_all_time_v2(self):
        while True:
            r = self.analyze_task_v2()
            if r == 0:
                time.sleep(60)


if __name__ == '__main__':
    TS = TaskService()
    TS.run_all_time()
