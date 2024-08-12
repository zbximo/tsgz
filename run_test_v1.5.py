# -*- encoding: utf-8 -*-
# @ModuleName: test11
# @Author: ximo
# @Time: 2024/5/27 11:39
import time

import argparse
import os

from apscheduler.schedulers.background import BackgroundScheduler


def main():
    parser = argparse.ArgumentParser(description='Script description')

    parser.add_argument('--name', type=str, nargs='+', help='name:{cluster, new, post}',
                        choices=["cluster", "new", "post"])
    parser.add_argument('--env', type=str, help='test', default='test', choices=["test"])
    # parser.add_argument('--env', type=str, help='test、product', default='test', choices=["test", "product"])

    args = parser.parse_args()
    name = args.name
    mode = args.env
    assert name and len(name) > 0, "Please add task name"

    from services_pro.TaskService import TaskService
    from services_pro.NewsService import NewsService
    from services_pro.SocialPostService import SocialPostService
    os.environ["tsgz_mode"] = mode
    # if 'cluster' in name:
    #     ts = TaskService(mode)
    #     ts.run_all_time_v2()
    #
    # if 'new' in name:
    #     ns = NewsService(mode)
    #     ns.run_all_time()
    #
    # if 'post' in name:
    #     sps = SocialPostService(mode)
    #     sps.run_all_time()
    scheduler = BackgroundScheduler()

    if 'cluster' in name:
        ts = TaskService(mode)
        scheduler.add_job(ts.analyze_task_v2, 'interval', minutes=1)
    if 'new' in name:
        ns = NewsService(mode)
        scheduler.add_job(ns.senti_news, 'interval', minutes=1)
    if 'post' in name:
        sps = SocialPostService(mode)
        scheduler.add_job(sps.senti_post, 'interval', minutes=1)
    scheduler.start()


if __name__ == '__main__':
    try:
        main()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        exit(1)
