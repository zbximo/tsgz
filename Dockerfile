# 使用官方的 Anaconda 基础镜像

FROM python3.10-torch2.3.0-cuda12.1-cudnn8-paddle2.6.1:v2
ENV PATH="/opt/conda/bin:${PATH}"
EXPOSE 5000
## 设置工作目录
WORKDIR /tsgz
#
## 复制项目文件
COPY . .

# RUN pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/


## 运行项目
CMD ["python", "app.py"]
