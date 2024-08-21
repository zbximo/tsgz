# -*- encoding: utf-8 -*-
# @ModuleName: TaskService
# @Author: ximo
# @Time: 2024/5/9 11:04

from sqlalchemy import and_, case
from sqlalchemy.orm import Query
from tqdm import tqdm
import paddlenlp

import log_pro
from db.entity import *
from models.Cluster import *
from models.EventCls import EventCls
from utils.Tools import *
import numpy as np
import transformers
transformers.logging.set_verbosity_error()

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

        cluster = Cluster()
        cluster.load_text_emb(device='cuda:1')
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
                insert_data = []

                for i in news_list:
                    data_tmp = {"id": i.id, "title": i.title, "content": i.content}
                    if i.title is None or i.title == "":
                        data_tmp["title"] = " "
                    if i.content is None or i.content == "":
                        data_tmp["content"] = " "

                    insert_data.append(data_tmp)
                # with open("r.json","w") as f:
                #     f.write(str(insert_data))
                # insert_data = [
                #     {"id": i.id, "title": i.title, "content": i.content} if i.title is not None and i != "" else {
                #         "id": i.id, "title": " ", "content": i.content} for i in news_list]
                news_zh_titles = [j.title if j.title is not None and j.title != "" else " " for j in news_list]
                news_id = [j.id for j in news_list]

                e_session = self.db.get_new_session()

                events = e_session.query(DataEvent).filter(
                    DataEvent.plan_id == task.plan_id).order_by(
                    case(
                        [(DataEvent.title == '非事件信息', 1)],
                        else_=0
                    ).asc(),
                ).all()

                event_id_titles = [[j.id, j.title] for j in events]
                EC = EventCls()
                EC.insert_milvus(task.plan_id, insert_data)
                data_by_event, titles_data_by_event = EC.predict(event_id_titles, task.keywords.split(","),
                                                                 news_zh_titles, news_id)
                # ori_data_by_event = {}
                # 遍历添加data_add表
                batch_size = 100  # 每N个记录提交一次
                count = 0
                add_session = self.db.get_new_session()
                for e_id, new_ids in data_by_event.items():
                    for nid in new_ids:
                        dataAddid = snowflake.generate()
                        dataAdd = DataAdd()
                        dataAdd.id = dataAddid
                        dataAdd.task_id = task.id
                        dataAdd.plan_id = task.plan_id
                        dataAdd.newsId = nid
                        dataAdd.event_id = e_id
                        count += 1
                        add_session.add(dataAdd)
                        if count % batch_size == 0:
                            add_session.commit()
                if count % batch_size != 0:
                    add_session.commit()
                add_session.close()
                e_session.close()
                EC.close()
                del EC
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
                    DataSimilarsIds = [i.id for i in DataSimilars]  # [DataSimilars.id,...]
                    DataSimilarsNewsIds = [eval(i.news_ids) for i in DataSimilars]  # [[DataSimilars.news.id,...],]
                    # 返回的data_by_event,包含所有事件,会存在一条新闻没被分类到某个事件的情况
                    if len(v)==0:
                        continue
                    # 没有相似文章 直接聚类
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

                        dsnewsids = [d[0] for d in DataSimilarsNewsIds]  # 拿出每一个类的第一条新闻ID [news.id,...]
                        similar_news = q_session.query(DataNew.title).filter(
                            DataNew.id.in_(dsnewsids)).all()
                        similar_news_list = [title[0] for title in similar_news]  # [news.title,...]
                        similar_news_emb_list = cluster.get_embedding(
                            similar_news_list)  # [news.embedding, ...] [n,768]
                        for i, t in tqdm(zip(data_by_event[k], titles_data_by_event[k])):
                            source = cluster.get_embedding(t)
                            # similar_matrix, score = cluster.similarity(t, similar_news_list,
                            #                                            threshold=threshold, use_emd=True)
                            similar_matrix, score = cluster.similarity(source, similar_news_emb_list,
                                                                       threshold=threshold, use_emd=False)
                            # 能在现有数据中匹配到相似文章
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
                                dsnewsids.append(i)
                                similar_news_list.append(t)

                                similar_news_emb_list = np.append(similar_news_emb_list, source, axis=0)

                    q_session.commit()
                q_session.close()

            if post_id_list is not None and len(post_id_list) != 0:
                posts_query: Query = session.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list))
                posts_list = posts_query.all()
                insert_data = [{"id": i.id, "title": i.title} if i.title is not None and i != "" else {
                    "id": i.id, "title": " "} for i in posts_list]
                post_zh_titles = [j.title if j.title is not None and j.title != "" else " " for j in posts_list]
                post_id = [j.id for j in posts_list]
                e_session = self.db.get_new_session()

                events = e_session.query(DataEvent).filter(
                    DataEvent.plan_id == task.plan_id).order_by(
                    case(
                        [(DataEvent.title == '非事件信息', 1)],
                        else_=0
                    ).asc(),
                ).all()

                event_id_titles = [[j.id, j.title] for j in events]
                EC = EventCls()
                EC.insert_milvus(task.plan_id, insert_data, is_news=False)
                data_by_event, titles_data_by_event = EC.predict(event_id_titles, task.keywords.split(","),
                                                                 post_zh_titles, post_id)
                # ori_data_by_event = {}
                # 遍历添加data_add表
                batch_size = 100  # 每N个记录提交一次
                count = 0
                add_session = self.db.get_new_session()
                for e_id, p_ids in data_by_event.items():
                    for pid in p_ids:
                        dataAddid = snowflake.generate()
                        dataAdd = DataAdd()
                        dataAdd.id = dataAddid
                        dataAdd.task_id = task.id
                        dataAdd.plan_id = task.plan_id
                        dataAdd.postId = pid
                        dataAdd.event_id = e_id
                        add_session.add(dataAdd)
                        if count % batch_size == 0:
                            add_session.commit()
                if count % batch_size != 0:
                    add_session.commit()
                add_session.close()
                e_session.close()
                EC.close()
                del EC
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
    os.environ['tsgz_mode'] = "test"
    TS = TaskService('test')
    TS.run_all_time_v2()
    # TS.analyze_task_v2()
