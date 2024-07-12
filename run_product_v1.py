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
    parser.add_argument('--ssh', action='store_true', help='Enable ssh')
    parser.add_argument('--env', type=str, help='env', default='product', choices=["product"])

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
    use_ssh = args.ssh
    os.environ["tsgz_mode"] = mode
    # if name == 'cluster':
    #     ts = TaskService(mode, use_ssh=use_ssh)
    #     ts.run_all_time()
    # elif name == 'new':
    #     ns = NewsService(mode, use_ssh=use_ssh)
    #     ns.run_all_time()
    # elif name == 'post':
    #     sps = SocialPostService(mode, use_ssh=use_ssh)
    #     sps.run_all_time()
    # else:
    #     raise Exception('name is not support')
    if 'cluster' in name:
        ts = TaskService(mode, use_ssh=use_ssh)
        # ts.run_all_time()
        scheduler = BackgroundScheduler()
        scheduler.add_job(ts.analyze_task, 'interval', minutes=1)
        scheduler.start()
    if 'new' in name:
        ns = NewsService(mode, use_ssh=use_ssh)
        # ns.run_all_time()
        scheduler1 = BackgroundScheduler()
        scheduler1.add_job(ns.senti_news, 'interval', minutes=1)
        scheduler1.start()
    if 'post' in name:
        sps = SocialPostService(mode, use_ssh=use_ssh)
        # sps.run_all_time()
        scheduler2 = BackgroundScheduler()
        scheduler2.add_job(sps.senti_post, 'interval', minutes=1)
        scheduler2.start()

if __name__ == '__main__':
    main()
    while True:
        pass
