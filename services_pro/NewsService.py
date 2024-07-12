# -*- encoding: utf-8 -*-
# @ModuleName: NewsService
# @Author: ximo
# @Time: 2024/5/10 11:21
import time
from tqdm import tqdm

import log_pro
from db.database import dbTools
from db.entity import *
from models.SentimentCls import SentimentCls
from sqlalchemy.orm.query import Query
import constants
import os

class NewsService():
    def __init__(self, mode='pro',use_ssh=False):
        self.db = dbTools(mode)
        self.db.open(use_ssh=use_ssh)
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def senti_news(self):
        session = self.db.get_new_session()
        query: Query = session.query(DataNew).filter(DataNew.is_emotional_analysed == 0)
        # query: Query = session.query(DataNew)

        num = query.count()
        self.log_pro.info(num)
        if num == 0:
            session.close()
            return 0
        SC = SentimentCls()

        bs = 100
        for i in tqdm(range(0, num, bs)):
            # result = query.offset(i).limit(bs).all()
            result = query.limit(bs).all()
            original_titles = [ii.original_title[:100] if ii.original_title is not None else " " for ii in result]
            titles = [ii.title[:100] if ii.title is not None else " " for ii in result]

            try:
                analyzed = SC.predict(original_titles, titles)
                for one, emo in zip(result, analyzed):
                    one.emotion = constants.Sentiment.senti[emo]
                    one.is_emotional_analysed = 1
            except Exception as e:
                self.retry_senti(result)
            finally:
                session.commit()
        session.close()
        return 1

    def run_all_time(self):
        while True:
            r = self.senti_news()
            if r == 0:
                time.sleep(60)

    def retry_senti(self, result):
        SCR = SentimentCls()
        for one in result:
            one.is_emotional_analysed = 1
            try:
                emo = SCR.predict(one.original_title, one.title)
                one.emotion = constants.Sentiment.senti[emo]
            except:
                one.emotion = constants.Sentiment.senti["neutral"]



if __name__ == '__main__':
    news = NewsService()
    r = news.run_all_time()
