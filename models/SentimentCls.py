# -*- encoding: utf-8 -*-
# @ModuleName: SentimentCls
# @Author: ximo
# @Time: 2024/5/10 10:56

from paddlenlp import Taskflow

import config


class SentimentCls(object):
    def __init__(self):

        self.cn_model_path = config.MODEL_CONFIG["cn"]
        self.cn_schema = ["涉及中国", "不涉及中国"]
        self.cn_model = Taskflow("zero_shot_text_classification", schema=self.cn_schema, single_label=True,
                                 device_id=1,
                                 task_path=self.cn_model_path)

        self.emotion_model_path = config.MODEL_CONFIG["emotion"]
        self.emotion_schema = ["中立", "正面", "负面"]
        self.sentiment_classifier = Taskflow("zero_shot_text_classification", schema=self.emotion_schema, single_label=True,
                                             device_id=1,
                                             task_path=self.emotion_model_path)

    def predict(self, titles):
        if isinstance(titles, str):
            titles = [titles]
        elif isinstance(titles, list):
            pass
        else:
            raise ValueError("data type error")
        in_cn = self.cn_model(titles)

        emotion = self.sentiment_classifier(titles)

        labels = []

        for i, j in zip(in_cn, emotion):
            cn_label, cn_score = i["predictions"][0]["label"], i["predictions"][0]["score"]
            emo_label, emo_score = j["predictions"][0]["label"], j["predictions"][0]["score"]
            if cn_score > 0.7 and cn_label == "涉及中国":
                label1 = "涉及中国"
            else:
                label1 = "不涉及中国"
            label2 = emo_label if emo_score > 0.7 else "中立"
            if label1 == "不涉及中国":
                labels.append("中立")
            else:
                labels.append(label2)
        return labels


if __name__ == '__main__':
    titles = ["江西省气象台变更暴雨橙色预警信号- DoNews快讯"*10, "浙江人很友善","檢총장, 金여사 명품백 의혹에 “법리따라 엄정수사…지켜봐달라”","" ]
    x = [i if i is not None and i != "" else " " for i in titles]
    d = SentimentCls().predict(x)
    print(d)
