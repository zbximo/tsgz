# -*- encoding: utf-8 -*-
# @ModuleName: SocialPostService
# @Author: ximo
# @Time: 2024/5/10 14:13
import json
import time

from kafka import KafkaConsumer
from tqdm import tqdm

import config
import log_pro
from db.database import dbTools
from db.entity import *
from models.SentimentCls import SentimentCls
from sqlalchemy.orm.query import Query
import constants
import os


class SocialPostService():
    def __init__(self, mode='test'):
        self.db = dbTools(mode)
        self.db.open()
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def senti_post(self):
        session = self.db.get_new_session()
        query: Query = session.query(DataSocialPost).filter(DataSocialPost.is_Emotional_Analysed == 0)
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
            # original_titles = [ii.original_title[:200] if ii.original_title is not None else " " for ii in result]
            titles = [ii.title[:200] if ii.title is not None and ii.title != "" else " " for ii in result]
            try:
                analyzed = SC.predict(titles)

                for one, emo in zip(result, analyzed):
                    one.emotion = constants.Sentiment.senti[emo]
                    one.is_Emotional_Analysed = 1

            except Exception as e:
                self.retry_senti(result)

            finally:
                session.commit()
        session.close()
        return num

    def retry_senti(self, result):
        SCR = SentimentCls()
        for one in result:
            one.is_Emotional_Analysed = 1
            try:
                emo = SCR.predict(one.title)
                one.emotion = constants.Sentiment.senti[emo]
            except:
                one.emotion = constants.Sentiment.senti["neutral"]

    def run_all_time(self):
        while True:
            r = self.senti_post()
            if r == 0:
                time.sleep(60)

    def sent(self, data):
        title_list = [i.get("title", " ")[:100] if i is not None and i != "" else " " for i in data]
        id_list = [i.get("id") if i is not None and i != "" else " " for i in data]

        SC = SentimentCls()
        analyzed = SC.predict(title_list)
        session = self.db.get_new_session()
        updates = [{"id": news_id, "emotion": constants.Sentiment.senti[emo], "is_Emotional_Analysed": 1} for
                   news_id, emo in
                   zip(id_list, analyzed)]
        session.bulk_update_mappings(DataSocialPost, updates)
        session.commit()
        session.close()
        del SC

    def kafka_senti(self):
        consumer = KafkaConsumer(
            'NEW_POST',
            bootstrap_servers=config.KAFKA_CONFIG.get("bootstrap_servers"),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='post_consumer1',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        try:
            while True:
                messages = consumer.poll(timeout_ms=1000, max_records=100)
                data = [m.value for msgs in messages.values() for m in msgs]
                try:
                    if len(data) != 0:
                        self.sent(data)
                except Exception as e:
                    self.log_pro.error(f"{e=}")
        except KeyboardInterrupt:
            print("停止消费者...")
        finally:
            consumer.close()


if __name__ == '__main__':
    os.environ["tsgz_mode"] = "test"
    SPS = SocialPostService(mode="test")
    r = SPS.run_all_time()
