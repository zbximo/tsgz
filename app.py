# -*- encoding: utf-8 -*-
# @ModuleName: app
# @Author: ximo
# @Time: 2024/5/27 16:55
import log_pro
import argparse

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
import os

app = Flask(__name__)


def run(mode, name):
    from services_pro.TaskService import TaskService
    from services_pro.NewsService import NewsService
    from services_pro.SocialPostService import SocialPostService
    os.environ["tsgz_mode"] = mode
    scheduler = BackgroundScheduler()
    if name is None:
        name = ["cluster", "new", "post"]

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

def run_kafka(mode, name):
    from services_pro.TaskService import TaskService
    from services_pro.NewsService import NewsService
    from services_pro.SocialPostService import SocialPostService
    import threading
    os.environ["tsgz_mode"] = mode


    if name is None:
        name = ["cluster", "new", "post"]

    if 'cluster' in name:
        ts = TaskService(mode)
        p = threading.Thread(target=ts.kafka_analyze)
        p.start()
    if 'new' in name:
        ns = NewsService(mode)
        p = threading.Thread(target=ns.kafka_senti)
        p.start()
    if 'post' in name:
        sps = SocialPostService(mode)
        p = threading.Thread(target=sps.kafka_senti)
        p.start()


@app.route("/tasks", methods=["GET"])
def index():
    return jsonify(
        {
            "code": 200,
            "msg": "success",
        }
    )


def parse_args():
    parser = argparse.ArgumentParser(description='Flask Application')
    parser.add_argument('--host', default='0.0.0.0', help='The host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='The port to bind to')
    parser.add_argument('--env', type=str, default="test", help='select env', choices=["product", "test"])
    parser.add_argument('--name', type=str, nargs='+', help='name:{cluster, new, post}',
                        choices=["cluster", "new", "post"])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run_kafka(args.env, args.name)
    app.run(host=args.host, port=args.port)
