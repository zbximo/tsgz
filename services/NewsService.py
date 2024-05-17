# -*- encoding: utf-8 -*-
# @ModuleName: NewsService
# @Author: ximo
# @Time: 2024/5/10 11:21
import time

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
        for i in range(0, num, 10):
            qq = query.offset(i).limit(10)
            result = qq.all()
            content = [ii.original_title if ii.original_title else "" for ii in result]
            try:
                analyzed = SC.predict(content)
                for one, emo in zip(result, analyzed):
                    one: DataNew
                    one.emotion = constants.Sentiment.senti[emo]
            except Exception as e:
                print(i, "error")
                print(e)
                pass
            # i.is_emotional_analysed
            self.db.commit()
        return num

    def close(self):
        self.db.close()


if __name__ == '__main__':
    news = NewsService()
    r = news.senti_news()
    news.close()
