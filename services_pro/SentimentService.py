# -*- encoding: utf-8 -*-
# @ModuleName: SentimentService
# @Author: ximo
# @Time: 2024/9/19 14:22

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


class SentimentService():
    def __init__(self, mode='test'):
        self.db = dbTools(mode)
        self.db.open()
        self.log_pro = log_pro.log_with_name(f"{os.environ['tsgz_mode']}")

    def kafka_senti(self):
        topic2orm = {'NEW_NEW': DataNew,
                     'NEW_POST': DataSocialPost,
                     'NEW_POST_COMMENT': DataSocialComment
                     }

        consumer = KafkaConsumer(
            bootstrap_servers=config.KAFKA_CONFIG.get("bootstrap_servers"),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='post_consumer1',
            # value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        consumer.subscribe(['NEW_NEW', 'NEW_POST', 'NEW_POST_COMMENT'])

        SC = SentimentCls()
        while True:
            messages = consumer.poll(timeout_ms=1000, max_records=500)
            # data = [m.value for msgs in messages.values() for m in msgs]
            id_list = []
            title_list = []
            type_list = []
            for partition, records in messages.items():
                for message in records:
                    try:
                        msg = json.loads(message.value.decode('utf-8'))
                        if msg is not None and "id" in msg.keys():
                            if "title" in msg.keys():
                                _key = "title"
                            else:
                                _key = "comment_content"
                            title = msg.get(_key, " ")
                            if title == "":
                                title = " "
                            title_list.append(title[:100])
                            id_list.append(msg.get("id"))
                            type_list.append(message.topic)
                    except Exception as e:
                        print(f"Failed to decode message at offset {message.offset}. Error: {e}")
            if len(title_list) > 0:
                analyzed = SC.predict(title_list)
                update_dict = {
                    'NEW_NEW': [], 'NEW_POST': [], 'NEW_POST_COMMENT': []
                }
                for tb, news_id, emo in zip(type_list, id_list, analyzed):
                    update_dict[tb].append(
                        {"id": news_id, "emotion": constants.Sentiment.senti[emo], "is_Emotional_Analysed": 1})
                for tb, updates in update_dict.items():
                    try:
                        session = self.db.get_new_session()
                        session.bulk_update_mappings(topic2orm[tb], updates)
                        session.commit()
                        session.close()
                    except Exception as e:
                        print(f"update error:{e}")
                    # print(tb, updates)


if __name__ == '__main__':
    os.environ["tsgz_mode"] = "test"
    SS = SentimentService(mode="test")
    r = SS.kafka_senti()
