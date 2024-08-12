# -*- encoding: utf-8 -*-
# @ModuleName: EventCls
# @Author: ximo
# @Time: 2024/5/14 14:53

import paddlenlp
from paddlenlp import Taskflow
import config


class EventCls():
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["utc-base"]):
        self.MODEL_PATH = MODEL_PATH
        self.cls = None
        self.schema = None

    def load(self, schema):
        # schema = ["政治变动", "军事冲突", "科技创新", "经济发展", "文化娱乐", "自然灾害", "事故灾难", "公共卫生",
        #           "社会安全"]
        self.schema = schema
        self.cls = Taskflow("zero_shot_text_classification", schema=schema, single_label=True, device_id=0,
                            task_path=self.MODEL_PATH)

    def predict(self, data):
        if isinstance(data, str):
            data = [data]
        elif isinstance(data, list):
            pass
        else:
            raise ValueError("data type error")
        result = self.cls(data)

        # max_indexs = []
        # max_score = []
        # for i in result:
        #     if i["predictions"][0]["score"]>threshold:
        #         max_indexs.append(self.schema.index(i["predictions"][0]["label"]))
        #     else:
        #         max_indexs.append(len(self.schema))
        #     max_score.append(i["predictions"][0]["score"])
        max_indexs = [self.schema.index(i["predictions"][0]["label"]) for i in result]
        max_score = [i["predictions"][0]["score"] for i in result]

        return max_indexs, max_score


if __name__ == '__main__':
    EC = EventCls()
    schema = ["美国大选投票统计", "遭遇枪击", "政策主张", "世界羽坛"]
    EC.load(schema)
    result = EC.predict(["特朗普，被枪击后被护送下台 - 照片捕捉到的事件的样子","aaaa"])
    print(result)
