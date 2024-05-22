# -*- encoding: utf-8 -*-
# @ModuleName: NewsService
# @Author: ximo
# @Time: 2024/5/10 11:21
import time
from tqdm import tqdm
from db.database import dbTools
from db.entity import *
from models.SentimentCls import SentimentCls
from sqlalchemy.orm.query import Query
import constants


class NewsService():
    def __init__(self):
        self.db = dbTools()
        self.db.open(use_ssh=True)

    def senti_news(self):
        SC = SentimentCls()
        query: Query = self.db.query(DataNew).filter(DataNew.is_emotional_analysed == 0)
        num = query.count()
        bs = 100
        for i in tqdm(range(0, num, bs)):
            # qq = query.offset(i).limit(100)
            # result = qq.all()
            result = query.limit(bs).all()
            content = [ii.original_title if ii.original_title else "" for ii in result]
            try:
                analyzed = SC.predict(content)
                for one, emo in zip(result, analyzed):
                    one.emotion = constants.Sentiment.senti[emo]
                    one.is_emotional_analysed = 1
            except Exception as e:
                self.retry_senti(result)
            finally:
                self.db.commit()

        return num

    def retry_senti(self, result):
        SCR = SentimentCls()
        for one in result:
            one.is_emotional_analysed = 1
            try:
                emo = SCR.predict(one.original_title)
                one.emotion = constants.Sentiment.senti[emo]
            except:
                one.emotion = constants.Sentiment.senti["neutral"]

    def close(self):
        self.db.close()


if __name__ == '__main__':
    news = NewsService()
    r = news.senti_news()
    news.close()
