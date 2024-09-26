# 态势感知


## V2.0

### 安装
- pip install torch==2.3.0 -i https://pypi.mirrors.ustc.edu.cn/simple/
- pip install paddlenlp==2.6.0 -i https://pypi.mirrors.ustc.edu.cn/simple/ 
- pip install paddlepaddle-gpu==2.6.1 -i https://pypi.mirrors.ustc.edu.cn/simple/
- pip install transformers==4.40.2 sentence_transformers==2.7.0 -i https://pypi.mirrors.ustc.edu.cn/simple/
- pip install scikit_learn==1.4.2 flask pymysql==1.1.0 sshtunnel tqdm SQLAlchemy==1.4.52 apscheduler -i https://pypi.mirrors.ustc.edu.cn/simple/

### 使用方法
#### 可选参数


以下是运行脚本时可以使用的可选参数说明：

| 参数               | 类型     | 默认值    | 描述                                                         | 可选值                          |
| ------------------ | -------- | --------- | ------------------------------------------------------------ | ------------------------------- |
| `--host`           | `string` | `'0.0.0.0'`| 要绑定的主机地址。                                           | 无                               |
| `--port`           | `int`    | `5000`    | 要绑定的端口号。                                             | 无                               |
| `--env`            | `string` | `'test'`  | 选择运行环境。                                               | `product`, `test`               |
| `--name`           | `string` | `None`    | 指定名称，支持多个值。                                        | `cluster`, `new`, `post`        |

#### 示例用法

运行脚本时，可以根据需要指定这些可选参数：

```bash
python sentiment.py --host 127.0.0.1 --port 5000 --env test --name cluster new
```
