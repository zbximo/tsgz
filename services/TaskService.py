# -*- encoding: utf-8 -*-
# @ModuleName: TaskService
# @Author: ximo
# @Time: 2024/5/9 11:04
from utils.Tools import *
from sqlalchemy.orm import Query
from sqlalchemy import func, or_, and_
from collections import Counter

from db.database import dbTools
from db.entity import *
from models.Cluster import *
import jieba


class TaskService():
    def __init__(self):
        self.db = dbTools()
        self.db.open(use_ssh=True)

    def analyze_task(self):

        task_query = self.db.query(DataTask)
        task_result = task_query.limit(10)
        with open("../baidu_stopwords.txt", "r") as f:
            stop_words = f.read().splitlines()
        cluster = Cluster()
        for task in task_result:
            task: DataTask
            post_id_list = eval(task.post_id_list) if task.post_id_list else None
            new_id_list = eval(task.news_id_list) if task.news_id_list else None

            # cluster and topic model for news
            news_query: Query = self.db.query(DataNew).filter(DataNew.id.in_(new_id_list))
            news = news_query.all()

            news_original_titles = [j.original_title for j in news]
            cluster_result = cluster.cluster_sentences(news_original_titles, threshold=1)

            for k, v in cluster_result.items():
                dataEvent = DataEvent()
                snowflake = SnowFlake()
                dataEvent.id = snowflake.generate()
                dataEvent.plan_id = task.plan_id
                dataEvent.task_id = task.id
                dataEvent.newsIds = str([news[index].id for index in v])
                # dataEvent.style

                # 分词,统计词频
                data = "。".join([news[index].title for index in v])
                seg_list = jieba.cut(data)
                words = [word for word in seg_list if word not in stop_words]
                word_counts = Counter(words)
                top_words = [word for word, count in word_counts.most_common(3)]
                filters = [DataSocialPost.title.contains(word) for word in top_words]

                # 在Posts中搜索关键词
                post_query = self.db.query(DataSocialPost).filter(DataSocialPost.id.in_(post_id_list)) \
                    .filter(and_(*filters)).all()
                dataEvent.postIds = str([p.id for p in post_query])
                self.db.add(dataEvent)
                print(dataEvent.__dict__)
                self.db.commit()
                # break
            break

    # @staticmethod
    # def get_task():
    #     db = DB()
    #     db.connect()
    #     task_service = TaskService()
    #     task_service.task(db)
    #     db.close()


if __name__ == '__main__':
    TS = TaskService()
    TS.analyze_task()
