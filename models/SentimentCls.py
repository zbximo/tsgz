# -*- encoding: utf-8 -*-
# @ModuleName: SentimentCls
# @Author: ximo
# @Time: 2024/5/10 10:56
import time

from transformers import pipeline

import config
from paddlenlp import Taskflow


class SentimentCls(object):
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["sentiment"], ZERO_SHOT=config.MODEL_CONFIG["utc-base"],
                 ):
        self.MODEL_PATH = MODEL_PATH

        self.sentiment_classifier = pipeline(
            "text-classification",
            self.MODEL_PATH,
            # return_all_scores=True,
            device=0
        )

        self.ZERO_SHOT = ZERO_SHOT
        schema = ["涉及中国", "不涉及中国"]
        self.cls = Taskflow("zero_shot_text_classification", schema=schema, single_label=True, device_id=0,
                            task_path=self.ZERO_SHOT)

    def predict(self, original_titles, titles):
        """

        :param original_titles: 原始标题
        :param titles: 翻译后的标题
        :return:
        """
        if isinstance(original_titles, str):
            original_titles = [original_titles]
            titles = [titles]
        elif isinstance(original_titles, list):
            pass
        else:
            raise ValueError("data type error")
        in_china = self.cls(titles)

        result = self.sentiment_classifier(original_titles)

        labels = []

        for i, j in zip(in_china, result):
            label1 = i["predictions"][0]["label"]
            if i["predictions"][0]["score"] > 0.7 and label1 == "涉及中国":
                label1 = "涉及中国"
            else:
                label1 = "不涉及中国"
            label2 = j["label"] if j["score"] > 0.7 else "neutral"
            # print(i, j)
            if label1 == "不涉及中国":
                labels.append("neutral")
            else:
                labels.append(label2)
        # labels = [i["label"] if i["score"] > 0.8 else "neutral" for i in result]
        return labels


if __name__ == '__main__':
    data = ["Zhejiang Province held the Olympic Games today", " ", ]
    titles = ["江西省气象台变更暴雨橙色预警信号- DoNews快讯", " ", ]
    d = SentimentCls().predict(data, titles)
    print(d)
