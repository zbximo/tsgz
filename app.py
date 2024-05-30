# -*- encoding: utf-8 -*-
# @ModuleName: app
# @Author: ximo
# @Time: 2024/5/27 16:55


from flask import Flask, request, jsonify
from services.TaskService import TaskService

app = Flask(__name__)


@app.route("/tasks", methods=["GET"])
def index():
    args = request.args

    # 从查询参数中获取特定的参数值
    id = args.get('method_id')
    plan_id = args.get('plan_id')
    ts = TaskService()
    # ts.analyze_task(id=1, plan_id=20)
    r = ts.analyze_task(id=id, plan_id=plan_id)
    if r == 1:
        return jsonify(
            {
                "code": 200,
                "msg": "success",
                "data": {'id': id, 'plan_id': plan_id}
            }
        )
    else:
        return jsonify(
            {
                "code": 200,
                "msg": "fail",
            }
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
