# 使用官方的 Anaconda 基础镜像

FROM nvcr.io/nvidia/cuda12.1.0-cudnn8-devel-ubuntu20.04

## 设置工作目录
WORKDIR /tsgz
#
## 复制项目文件
COPY . .

RUN pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/



# 运行项目
CMD ["python", "app.py"]
