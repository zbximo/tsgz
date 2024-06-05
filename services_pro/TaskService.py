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
import log_pro
import os
class TaskService():
    def __init__(self, mode='pro'):
        self.db = dbTools(mode)
        self.db.open(use_ssh=True)
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def analyze_task(self):
        self.db.get_new_session()
        task_query = self.db.query(DataTask).filter(and_(DataTask.status == 0))
        task_result = task_query.all()
        # print(f'{task_result=}')
        self.log_pro.info(len(task_result))

        if len(task_result) == 0:

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

            # cluster and topic model for news
            news_query: Query = self.db.query(DataNew).filter(DataNew.id.in_(new_id_list))
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
                cluster_news_result = cluster.cluster_sentences(news_ori_titles, threshold=1) \
                    if len(news_ori_titles) > 1 else {0: [0]}
                for ck, cv in cluster_news_result.items():
                    dataSimilar = DataSimilar()
                    dataSimilar.id = snowflake.generate()
                    dataSimilar.plan_id = task.plan_id
                    dataSimilar.news_ids = str([news_ids[cindex] for cindex in cv])
                    dataSimilar.event_id = dataEventid
                    self.db.add(dataSimilar)

                # 分词,统计词频
                data = "。".join(news_titles)
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
            task.status = 1
            self.db.commit()
            self.log_pro.info(f'{task.id=} over')
            self.db.close()
        return 1

    def run_all_time(self):
        while True:
            r = self.analyze_task()
            if r == 0:
                time.sleep(60)


if __name__ == '__main__':
    TS = TaskService()
    TS.run_all_time()
