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

mode = 'test'
db = dbTools(mode)
db.open(use_ssh=True)
q_session = db.get_new_session()
new = q_session.query(DataEvent).filter(and_(DataEvent.prediction == None, DataEvent.title != "非事件信息")).all()
for i in new:
    print(i.__dict__)
q_session.close()

# news = q_session.query(DataNew).filter(DataNew.id.in_([2, 3, 4])).all()
#
# for i in news:
#     print(111,i.__dict__)
#     i.title = str(i.title)[:-1]
#     q_session.commit()
#     print(112,i.__dict__)
# time.sleep(10)
# for i in news:
#     print(211,i.__dict__)
#     i.title = str(i.title)[:-1]
#     q_session.commit()
#     print(222,i.__dict__)
# q_session.close()
# q_session.commit()

# cluster = Cluster()
# cluster.load_text_emb()
# cluster.get_embedding(["我的你的好的"]*100).tolist()


# from services_pro.TaskService import TaskService
# from services_pro.NewsService import NewsService
# from services_pro.SocialPostService import SocialPostService
# import time
# #
# # #
# os.environ["tsgz_mode"] = "test_v2"
# ts = TaskService("test", use_ssh=True)
# while True:
#     ts.analyze_task_v2()
#     time.sleep(60)


# from  utils import Tools
# Tools.db2model()
