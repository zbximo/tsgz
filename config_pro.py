# -*- encoding: utf-8 -*-
# @ModuleName: config
# @Author: ximo
# @Time: 2024/5/8 13:42


# SSH 隧道配置
SSH_CONFIG = {
    'host': '10.63.146.221',
    'port': 8203,
    'username': 'lenovo3',
    'password': 'tsgz2024',
}

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'username': 'root',
    'password': 'tsgz2024',
    'database': 'situation_system'
}

# 模型路径配置
MODEL_CONFIG = {
    "sentiment": "/mnt/data/users/xhd/xl/models/models--lxyuan--distilbert-base-multilingual-cased-sentiments-student/snapshots/2e33845d25b3ed0c8994ed53adb72566a1d39d79",
    "text_emb": "/mnt/data/users/xhd/xl/models/models--sentence-transformers--LaBSE/snapshots/50fe0940fa3ca3be4d2170f21395beb6d581fc44",
    "event_cls": "/home/amax/.paddlenlp/taskflow/zero_shot_text_classification/utc-base",
    "lac": "/home/amax/.paddlenlp/taskflow/lac"
}
