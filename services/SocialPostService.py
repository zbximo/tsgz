# -*- encoding: utf-8 -*-
# @ModuleName: SocialPostService
# @Author: ximo
# @Time: 2024/5/10 14:13


from db.database import dbTools
from db.entity import *
from models.SentimentCls import SentimentCls
from sqlalchemy.orm.query import Query
import constants


class SocialPostService():
    def __init__(self):
        self.db = dbTools()
        self.db.open(use_ssh=True)

    def senti_post(self):
        SC = SentimentCls()
        query: Query = self.db.query(DataSocialPost).filter(DataSocialPost.is_Emotional_Analysed == 0)
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
            # i.is_emotional_analysed
            self.db.commit()
        return num

    def close(self):
        self.db.close()


if __name__ == '__main__':
    SPS = SocialPostService()
    r = SPS.senti_post()
    SPS.close()
