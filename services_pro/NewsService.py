# -*- encoding: utf-8 -*-
# @ModuleName: NewsService
# @Author: ximo
# @Time: 2024/5/10 11:21
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


class NewsService():
    def __init__(self, mode='test'):
        self.db = dbTools(mode)
        self.db.open()
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
            # original_titles = [ii.original_title[:100] if ii.original_title is not None else " " for ii in result]
            titles = [ii.title[:100] if ii.title is not None and ii.title != "" else " " for ii in result]

            try:
                analyzed = SC.predict(titles)
                for one, emo in zip(result, analyzed):
                    one.emotion = constants.Sentiment.senti[emo]
                    one.is_emotional_analysed = 1
            except Exception as e:
                self.retry_senti(result, SC)
            finally:
                session.commit()
        session.close()
        del SC
        return 1

    def run_all_time(self):
        while True:
            r = self.senti_news()
            if r == 0:
                time.sleep(60)

    def retry_senti(self, result, model):
        for one in result:
            one.is_emotional_analysed = 1
            try:
                emo = model.predict(one.title)
                one.emotion = constants.Sentiment.senti[emo]
            except:
                print(f'{one.title=}')
                one.emotion = constants.Sentiment.senti["neutral"]

    def sent(self, data):
        title_list = []
        id_list = []
        for i in data:
            if i is not None and i != "" and "id" in i.keys():
                title_list.append(i.get("title", " ")[:100])
                id_list.append(i.get("id"))

        SC = SentimentCls()
        analyzed = SC.predict(title_list)
        session = self.db.get_new_session()
        updates = [{"id": news_id, "emotion": constants.Sentiment.senti[emo], "is_emotional_analysed": 1} for
                   news_id, emo in zip(id_list, analyzed)]
        session.bulk_update_mappings(DataNew, updates)
        session.commit()
        session.close()
        self.log_pro.info(f"news count: {len(data)}")
        del SC

    def kafka_senti(self):
        consumer = KafkaConsumer(
            'NEW_NEW',
            bootstrap_servers=config.KAFKA_CONFIG.get("bootstrap_servers"),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='news_consumer1',
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
    news = NewsService(mode="test")
    r = news.run_all_time()
