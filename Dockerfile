# 使用官方的 Anaconda 基础镜像

FROM python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2.0
ENV PATH="/opt/conda/bin:${PATH}"
EXPOSE 5010
EXPOSE 5011
## 设置工作目录
WORKDIR /tsgz
#
## 复制项目文件
COPY . .



