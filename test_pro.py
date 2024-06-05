# -*- encoding: utf-8 -*-
# @ModuleName: test11
# @Author: ximo
# @Time: 2024/5/27 11:39
import time

import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Script description')

    parser.add_argument('--name', type=str, help='name:{cluster, new, post}', choices=["cluster", "new", "post"])
    parser.add_argument('--env', type=str, help='test、product', default='test', choices=["test", "product"])

    args = parser.parse_args()
    if args.name is None:
        raise Exception('name is required')
    from services_pro.TaskService import TaskService
    from services_pro.NewsService import NewsService
    from services_pro.SocialPostService import SocialPostService
    name = args.name
    mode = args.env
    os.environ["tsgz_mode"] = mode
    if name == 'cluster':
        ts = TaskService(mode)
        ts.run_all_time()
    elif name == 'new':
        ns = NewsService(mode)
        ns.run_all_time()
    elif name == 'post':
        sps = SocialPostService(mode)
        sps.run_all_time()
    else:
        raise Exception('name is not support')


if __name__ == '__main__':
    main()
