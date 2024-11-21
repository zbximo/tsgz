
log_dir="/mnt/data/users/xhd/tsgz_bak/logs_test"

docker run -v /mnt/data/users/xhd/tsgz:/tsgz \
  -v "$log_dir:/tsgz/logs" \
  --restart always \
  --name tsgz_sentiment_201 \
  -d --gpus all \
  -it --workdir /tsgz \
  python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2.0 \
  python sentiment.py --env product &

docker run -v /mnt/data/users/xhd/tsgz:/tsgz \
  -v "$log_dir:/tsgz/logs" \
  --restart always \
  --name tsgz_cluster_201 \
  -d --gpus all \
  -it --workdir /tsgz \
  python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2.0 \
  python cluster.py --env product