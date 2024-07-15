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
    print(args)
    if args.name is None:
        raise Exception('name is required')
    from services_pro.TaskService import TaskService
    from services_pro.NewsService import NewsService
    from services_pro.SocialPostService import SocialPostService
    name = args.name
    mode = args.env
    os.environ["tsgz_mode"] = mode
    if 'cluster' in name:
        ts = TaskService(mode, use_ssh=True)
        ts.run_all_time_v2()
        # scheduler = BackgroundScheduler()
        # ts.analyze_task_v2()
        # scheduler.add_job(ts.analyze_task_v2, 'cron', second='0/10')
        # scheduler.start()
    if 'new' in name:
        ns = NewsService(mode, use_ssh=True)
        ns.run_all_time()
        # scheduler1 = BackgroundScheduler()
        # scheduler1.add_job(ns.senti_news, 'interval', minutes=1)
        # scheduler1.start()
    if 'post' in name:
        sps = SocialPostService(mode, use_ssh=True)
        sps.run_all_time()
        # scheduler2 = BackgroundScheduler()
        # scheduler2.add_job(sps.senti_post, 'interval', minutes=1)
        # scheduler2.start()


if __name__ == '__main__':
    main()
    while True:
        pass

    
