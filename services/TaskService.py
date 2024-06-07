# -*- encoding: utf-8 -*-
# @ModuleName: TaskService
# @Author: ximo
# @Time: 2024/5/9 11:04
from utils.Tools import *
from sqlalchemy.orm import Query
from sqlalchemy import func, or_, and_, desc
from collections import Counter

from db.database import dbTools
from db.entity import *
from models.Cluster import *
import jieba


class TaskService():
    def __init__(self, mode='test'):
        self.db = dbTools(mode)
        self.db.open(use_ssh=True)

    def analyze_task(self, id=2, plan_id=None):
        if not plan_id:
            raise Exception("plan_id is None")
        session = self.db.get_new_session()
        task_query = session.query(DataTask).filter(and_(DataTask.status == 0, DataTask.plan_id == plan_id)).order_by(
            desc(DataTask.create_date))
        task_result = task_query.all()
        # with open("../utils/baidu_stopwords.txt", "r") as f:
        #     stop_words = f.read().splitlines()
        stop_words = get_stopwords()
        cluster = Cluster()
        cluster.load_text_emb()
        cluster.load_pos_model()
        for task in task_result:
            task: DataTask
            post_id_list = eval(task.post_id_list) if task.post_id_list else None
            new_id_list = eval(task.news_id_list) if task.news_id_list else None
            print("querying news......")

            # cluster and topic model for news
            news_query: Query = session.query(DataNew).filter(DataNew.id.in_(new_id_list))
            news = news_query.all()
            news_original_titles = [j.original_title for j in news]
            print("clustering ......")

            if id == 0:
                cluster_result = cluster.cluster_sentences(news_original_titles, threshold=1)
            elif id == 1:
                cluster_result = cluster.cluster_titles_agg(news_original_titles)
            else:
                cluster_result = cluster.cluster_titles_tfidf(news_original_titles)
            print("cluster over!")
            for k, v in cluster_result.items():
                dataEvent = DataEvent()
                snowflake = SnowFlake()
                dataEventid = snowflake.generate()
                dataEvent.id = dataEventid
                dataEvent.plan_id = task.plan_id
                dataEvent.task_id = task.id
                news_ids = [news[index].id for index in v]
                news_titles = [news[index].title for index in v]
                news_ori_titles = [news[index].original_title for index in v]
                dataEvent.newsIds = str(news_ids)
                # 识别相似新闻
                cluster_news_result = cluster.cluster_sentences(news_ori_titles, threshold=1) \
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
                word_counts = Counter(words)
                top_words = [word for word, count in word_counts.most_common(3)]
                filters = [DataSocialPost.title.contains(word) for word in top_words]
                # 在Posts中搜索关键词
                session_q = self.db.get_new_session()
                post_query = session_q.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list)) \
                    .filter(and_(*filters)).all()
                session_q.close()
                dataEvent.postIds = str([p.id for p in post_query])
                session.add(dataEvent)
            task.status = 1
            session.commit()
            session.close()
            break
        return 1


if __name__ == '__main__':
    TS = TaskService()
    # TS.analyze_task()
