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


def run_kafka(mode):
    from services_pro.TaskService import TaskService

    os.environ["tsgz_mode"] = mode

    ts = TaskService(mode)
    ts.kafka_analyze()


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
    parser.add_argument('--port', type=int, default=5011, help='The port to bind to')
    parser.add_argument('--env', default="test", type=str, help='env: test, product',
                        choices=["test", "product"])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run_kafka(args.env)
    app.run(host=args.host, port=args.port)
