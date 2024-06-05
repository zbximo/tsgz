# -*- encoding: utf-8 -*-
# @ModuleName: SocialPostService
# @Author: ximo
# @Time: 2024/5/10 14:13
import time

from tqdm import tqdm

import log_pro
from db.database import dbTools
from db.entity import *
from models.SentimentCls import SentimentCls
from sqlalchemy.orm.query import Query
import constants
import os

class SocialPostService():
    def __init__(self, mode='pro'):
        self.db = dbTools(mode)
        self.db.open(use_ssh=True)
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def senti_post(self):
        self.db.get_new_session()
        SC = SentimentCls()
        query: Query = self.db.query(DataSocialPost).filter(DataSocialPost.is_Emotional_Analysed == 0)
        # query: Query = self.db.query(DataSocialPost)

        num = query.count()
        # print('post total num:', num)
        self.log_pro.info(num)
        if num == 0:
            return 0
        bs = 100
        for i in tqdm(range(0, num, bs)):
            # result = query.offset(i).limit(bs).all()
            result = query.limit(bs).all()
            original_titles = [ii.original_title[:200] if ii.original_title is not None else " " for ii in result]
            titles = [ii.title[:200] if ii.title is not None else " " for ii in result]
            try:
                analyzed = SC.predict(original_titles, titles)

                for one, emo in zip(result, analyzed):
                    one.emotion = constants.Sentiment.senti[emo]
                    one.is_Emotional_Analysed = 1

            except Exception as e:
                self.retry_senti(result)

            finally:
                self.db.commit()
        self.db.close()
        return num

    def retry_senti(self, result):
        SCR = SentimentCls()
        for one in result:
            one.is_Emotional_Analysed = 1
            try:
                emo = SCR.predict(one.original_title, one.title)
                one.emotion = constants.Sentiment.senti[emo]
            except:
                one.emotion = constants.Sentiment.senti["neutral"]

    def run_all_time(self):
        while True:
            r = self.senti_post()
            if r == 0:
                time.sleep(60)

    def close(self):
        self.db.close()


if __name__ == '__main__':
    SPS = SocialPostService()
    r = SPS.run_all_time()
