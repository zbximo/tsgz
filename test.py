# # -*- encoding: utf-8 -*-
# # @ModuleName: test
# # @Author: ximo
# # @Time: 2024/5/20 15:12
#
# import argparse
#
# from services.TaskService import TaskService
#
#
# def main():
#     # 创建 ArgumentParser 对象
#     parser = argparse.ArgumentParser(description='Script description')
#
#     # 添加参数 method_id
#     parser.add_argument('--method_id', type=int, help='Method ID')
#
#     # 添加参数 plan_id
#     parser.add_argument('--plan_id', type=int, help='Plan ID')
#
#     # 解析命令行参数
#     args = parser.parse_args()
#
#     method_id = args.method_id
#     plan_id = args.plan_id
#     print(f'{method_id=},{plan_id=}')
#     if method_id is not None and plan_id is not None:
#         ts = TaskService()
#         ts.analyze_task(id=method_id, plan_id=plan_id)
#
#
# if __name__ == '__main__':
#     main()
from utils.Tools import *
from sqlalchemy.orm import Query
from sqlalchemy import func, or_, and_, desc, case
from collections import Counter

from db.database import dbTools
from db.entity import *
from models.Cluster import *
import jieba
import log_pro
import os

# mode = 'test'
# db = dbTools(mode)
# db.open(use_ssh=True)
# q_session = db.get_new_session()
# event = q_session.query(DataNew).filter(DataNew.id.in_([1802700762415558658, 1802737769285660673, 1802739316941893633])).all()
#


# for i in similar_news_list:
#     print(i)
# q_session.commit()
# for i in event:
#     print(i.plan_id,i.newsIds)

# q_session.commit()

# cluster = Cluster()
# cluster.load_text_emb()
# cluster.get_embedding(["我的你的好的"]*100).tolist()


from services_pro.TaskService import TaskService
from services_pro.NewsService import NewsService
from services_pro.SocialPostService import SocialPostService

#
os.environ["tsgz_mode"] = "test_v2"
ts = TaskService("test")
ts.analyze_task_v2()
