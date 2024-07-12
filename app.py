# -*- encoding: utf-8 -*-
# @ModuleName: app
# @Author: ximo
# @Time: 2024/5/27 16:55
import argparse

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
import os

from services_pro.TaskService import TaskService
from services_pro.NewsService import NewsService
from services_pro.SocialPostService import SocialPostService

app = Flask(__name__)


def run(ssh, mode):
    os.environ["tsgz_mode"] = mode
    print(f"{ssh=},{mode=}")
    ts = TaskService(mode, use_ssh=ssh)
    # ts.run_all_time_v2()
    scheduler = BackgroundScheduler()
    scheduler.add_job(ts.analyze_task_v2, 'interval', minutes=1)
    scheduler.start()
    ns = NewsService(mode, use_ssh=ssh)
    # ns.run_all_time()
    scheduler1 = BackgroundScheduler()
    scheduler1.add_job(ns.senti_news, 'interval', minutes=1)
    scheduler1.start()
    sps = SocialPostService(mode, use_ssh=ssh)
    # sps.run_all_time()
    scheduler2 = BackgroundScheduler()
    scheduler2.add_job(sps.senti_post, 'interval', minutes=1)
    scheduler2.start()


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
    parser.add_argument('--host', default='127.0.0.1', help='The host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='The port to bind to')
    parser.add_argument('--ssh', action='store_true', help='Enable ssh')
    parser.add_argument('--mode', type=str, default="test", help='Enable ssh',choices=["pro","test"])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run(args.ssh, args.mode)
    app.run(host=args.host, port=args.port)
