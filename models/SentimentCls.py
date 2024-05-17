# -*- encoding: utf-8 -*-
# @ModuleName: SentimentCls
# @Author: ximo
# @Time: 2024/5/10 10:56
from transformers import pipeline

import config


class SentimentCls(object):
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["sentiment"]):
        self.MODEL_PATH = MODEL_PATH

        self.sentiment_classifier = pipeline(
            "text-classification",
            self.MODEL_PATH,
            # return_all_scores=True,
            device=1
        )

    def predict(self, data):
        if isinstance(data, str):
            data = [data]
        elif isinstance(data, list):
            pass
        else:
            raise ValueError("data type error")
        result = self.sentiment_classifier(data)
        labels = [i["label"] if i["score"] > 0.8 else "neutral" for i in result]
        return labels


if __name__ == '__main__':
    data = SentimentCls().predict(["今天很开心"] * 3)
    print(data)
