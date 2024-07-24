# -*- encoding: utf-8 -*-
# @ModuleName: test11
# @Author: ximo
# @Time: 2024/5/27 11:39

import time

import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Script description')

    parser.add_argument('--name', type=str, nargs='+', help='name:{cluster, new, post}',
                        choices=["cluster", "new", "post"])
    parser.add_argument('--env', type=str, help='product', default='product', choices=["product"])
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
        ts = TaskService(mode, use_ssh=False)
        ts.run_all_time_v2()

    if 'new' in name:
        ns = NewsService(mode, use_ssh=False)
        ns.run_all_time()

    if 'post' in name:
        sps = SocialPostService(mode, use_ssh=False)
        sps.run_all_time()


if __name__ == '__main__':
    main()
    while True:
        pass



