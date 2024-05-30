# -*- encoding: utf-8 -*-
# @ModuleName: test
# @Author: ximo
# @Time: 2024/5/20 15:12

import argparse

from services.TaskService import TaskService


def main():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description='Script description')

    # 添加参数 method_id
    parser.add_argument('--method_id', type=int, help='Method ID')

    # 添加参数 plan_id
    parser.add_argument('--plan_id', type=int, help='Plan ID')

    # 解析命令行参数
    args = parser.parse_args()

    method_id = args.method_id
    plan_id = args.plan_id
    print(f'{method_id=},{plan_id=}')
    if method_id is not None and plan_id is not None:
        ts = TaskService()
        ts.analyze_task(id=method_id, plan_id=plan_id)


if __name__ == '__main__':
    main()
