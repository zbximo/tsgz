# -*- encoding: utf-8 -*-
# @ModuleName: analyze
# @Author: ximo
# @Time: 2024/5/20 15:12

import argparse


def main():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description='Script description')

    parser.add_argument('--name', type=str, help='name:{cluster, new, post}')

    parser.add_argument('--method_id', type=int, help='Method ID')

    parser.add_argument('--plan_id', type=int, help='Plan ID')

    parser.add_argument('--use_gpu', type=int, help='0:False, 1:True')
    # parser.print_help()
    parser.add_argument('--env', type=str, help='test、product', default='test', choices=["test", "product"])

    args = parser.parse_args()
    if args.name is None:
        raise Exception('name is required')
    from services.TaskService import TaskService
    from services.NewsService import NewsService
    from services.SocialPostService import SocialPostService
    name = args.name
    mode = args.env
    if name == 'cluster':
        method_id = args.method_id
        plan_id = args.plan_id
        print(f'{method_id=},{plan_id=}')
        if method_id is not None and plan_id is not None:
            ts = TaskService(mode)
            ts.analyze_task(id=method_id, plan_id=plan_id)
    elif name == 'new':
        ns = NewsService(mode)
        ns.senti_news()
    elif name == 'post':
        sps = SocialPostService(mode)
        sps.senti_post()


if __name__ == '__main__':
    main()
