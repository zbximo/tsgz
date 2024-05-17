# -*- encoding: utf-8 -*-
# @ModuleName: EventCls
# @Author: ximo
# @Time: 2024/5/14 14:53

import paddlenlp
from paddlenlp import Taskflow
import config


class EventCls():
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["event_cls"]):
        self.MODEL_PATH = MODEL_PATH
        schema = ["政治变动", "军事冲突", "科技创新", "经济发展", "文化娱乐", "自然灾害", "事故灾难", "公共卫生",
                  "社会安全"]

        self.cls = Taskflow("zero_shot_text_classification", schema=schema, single_label=True)

    def predict(self, data):
        if isinstance(data, str):
            data = [data]
        elif isinstance(data, list):
            pass
        else:
            raise ValueError("data type error")
        result = self.cls(data)
        print(result)
        labels = [i["predictions"][0]["label"] for i in result]
        return labels


if __name__ == '__main__':
    ec = EventCls()
    result = ec.predict("2023年3月8日，中国妇女权益保护法实施20周年。")
    print(result)
