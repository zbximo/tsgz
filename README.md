# 态势感知


## V2.0
### 运行环境
#### 显卡驱动
- 显卡驱动版本不小于535.129.03, 需支持cuda12.1, cudnn8.0
#### python环境
1. 本地自定义安装包
   - 具体见 requirements.txt
   - 安装方法: pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
2. docker镜像
### 数据库等配置
配置文件有config.py, config_pro.py，分别对应测试环境和生产环境。\
1. MILVUS
```
MILVUS_CONFIG = {
    'uri': 'http://10.63.146.221:19530',
    'user': "",
    'password': "",
    'db_name': "",
    'token': ""
}
```


2. MYSQL
```
DB_CONFIG = {
    'host': '10.63.146.221',
    'port': 33306,
    'username': 'root',
    'password': 'tsgz2024',
    'database': 'situation_system'
}
```

3. KAFKA
```
KAFKA_CONFIG = {
    'bootstrap_servers': ['10.63.146.203:9092'], 
    'topics': { #对应后端的topic
        'task': 'CHANGE_PLAN',  #聚类任务
        'news': 'NEW_NEW', #新闻
        'post': 'NEW_POST', #社媒
        'comment': 'NEW_POST_COMMENT' #社媒评论
    }

}
```
4. 在项目根目录创建model_dir文件夹, 将所有模型放入至model_dir文件夹中.目录结构如下:
```
./model_dir/
├── bce-embedding-base_v1
├── bce-reranker-base_v1
├── cn
├── emotion
├── nlp_structbert_zero-shot-classification_chinese-large
└── utc-base
```
### 启动命令
1. 聚类模型: `python clutser.py --env product`
2. 情感分析模型: `python sentiment.py --env product`

#### 可选参数

| 参数       | 类型     | 默认值    | 描述                                                     | 可选值                          |
|----------| -------- | --------- |--------------------------------------------------------| ------------------------------- |
| `--env`  | `string` | `'test'`  | 运行环境,`product`是对应config_pro配置文件, `test`对应config.py配置文件 | `product`, `test`               |

#### 用docker环境启动

```bash
log_dir="/mnt/data/users/projects/logs_test"
code_dir="/mnt/data/users/projects/tsgz"
docker run -v "$code_dir:/tsgz" \
  -v "$log_dir:/tsgz/logs" \
  --restart always \
  --name tsgz_sentiment_201 \
  -d --gpus all \
  -it --workdir /tsgz \
  python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2.0 \
  python sentiment.py --env product
  ```
```bash
log_dir="/mnt/data/users/projects/logs_test"
code_dir="/mnt/data/users/projects/tsgz"
docker run -v "$code_dir:/tsgz" \
  -v "$log_dir:/tsgz/logs" \
  --restart always \
  --name tsgz_sentiment_201 \
  -d --gpus all \
  -it --workdir /tsgz \
  python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2.0 \
  python sentiment.py --env product
  ```
