# -*- encoding: utf-8 -*-
# @ModuleName: config
# @Author: ximo
# @Time: 2024/5/8 13:42
import os


# # 数据库连接配置
MILVUS_CONFIG = {
    'host': '10.63.146.221',
    'port': 19530,
    # 'username': 'root',
    # 'password': 'tsgz2024',
    # 'database': 'situation_system'
}

# 数据库连接配置
DB_CONFIG = {
    'host': '10.63.146.221',
    'port': 33306,
    'username': 'root',
    'password': 'tsgz2024',
    'database': 'situation_system'
}


def get_model_dir(model_name):
    model_dir = os.path.join(os.path.dirname(__file__), f'model_dir/{model_name}')
    if os.path.exists(model_dir):
        return model_dir
    else:
        raise FileNotFoundError(f"Model directory for {model_name} not found.")


MODEL_CONFIG = {
    "sentiment": get_model_dir(
        "models--lxyuan--distilbert-base-multilingual-cased-sentiments-student/snapshots/2e33845d25b3ed0c8994ed53adb72566a1d39d79"),
    "text_emb": get_model_dir(
        "models--sentence-transformers--LaBSE/snapshots/50fe0940fa3ca3be4d2170f21395beb6d581fc44"),
    "utc-base": get_model_dir("utc-base"),
    "lac": get_model_dir("lac"),
    "cn": get_model_dir("cn"),
    "emotion": get_model_dir("emotion")
}
