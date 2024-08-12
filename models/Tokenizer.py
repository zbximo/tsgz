# -*- encoding: utf-8 -*-
# @ModuleName: Tokenizer
# @Author: ximo
# @Time: 2024/5/15 11:07
from transformers import AutoTokenizer
import config


class Tokenizer:
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["sentiment"]):
        self.MODEL_PATH = MODEL_PATH

        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_PATH)

    def tokenize(self, text):
        # 实现分词逻辑
        return self.tokenizer.tokenize(text)


if __name__ == '__main__':
    t = Tokenizer()
    r = t.tokenize("hello world")
    print(r)
