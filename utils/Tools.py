# -*- encoding: utf-8 -*-
# @ModuleName: Tools
# @Author: ximo
# @Time: 2024/5/9 11:12
import os
import subprocess
from db.database import dbTools
import time


def db2model():
    db = dbTools()
    r = db.open_ssh()
    print(r)

    sqlacodegen_command = f"""
    /opt/anaconda3/envs/tsgz/bin/sqlacodegen mysql+pymysql://root:tsgz2024@0.0.0.0:{r[1]}/situation_system --tables data_event,data_news,data_person,data_similar,data_social_comment,data_social_post,data_task --outfile /mnt/data/users/xhd/tsgz/db/entity.py"""
    print(sqlacodegen_command)
    result = subprocess.run(sqlacodegen_command, shell=True)
    print(result.returncode)
    db.close()


def get_stopwords():
    with open("baidu_stopwords.txt", "r") as f:
        stop_words = f.read().splitlines()
    return stop_words


class SnowFlake(object):
    def __init__(self, worker_id=1, datacenter_id=1, sequence=0):
        self.worker_id = worker_id  # 用于标识不同的工作机器
        self.datacenter_id = datacenter_id  # 用于标识不同的数据中心
        self.sequence = sequence  # 序列号，用于解决并发生成的 ID 冲突
        self.tw_epoch = 1288834974657  # Twitter Snowflake epoch (in milliseconds)，Snowflake 算法的起始时间点

        # Bit lengths，用于计算位数
        self.worker_id_bits = 5  # 5位，最大值为31
        self.datacenter_id_bits = 5  # 5位，最大值为31
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)  # 最大工作机器 ID
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)  # 最大数据中心 ID
        self.sequence_bits = 12  # 12位，支持的最大序列号数
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)  # 序列号掩码，用于生成序列号

        # Create initial timestamp，初始化上一次生成 ID 的时间戳
        self.last_timestamp = self.current_timestamp()

        # Check worker_id and datacenter_id values，检查工作机器 ID 和数据中心 ID 的取值范围
        if self.worker_id > self.max_worker_id or self.worker_id < 0:
            raise ValueError(f"Worker ID must be between 0 and {self.max_worker_id}")
        if self.datacenter_id > self.max_datacenter_id or self.datacenter_id < 0:
            raise ValueError(f"Datacenter ID must be between 0 and {self.max_datacenter_id}")

    @staticmethod
    def current_timestamp():
        return int(time.time() * 1000)  # 获取当前时间戳，单位为毫秒

    def generate(self):
        timestamp = self.current_timestamp()  # 获取当前时间戳

        if timestamp < self.last_timestamp:  # 如果当前时间戳小于上一次生成 ID 的时间戳
            raise ValueError("Clock moved backwards. Refusing to generate ID for {} milliseconds".format(
                self.last_timestamp - timestamp))  # 抛出异常，时钟回拨

        if timestamp == self.last_timestamp:  # 如果当前时间戳等于上一次生成 ID 的时间戳
            self.sequence = (self.sequence + 1) & self.sequence_mask  # 增加序列号，并与序列号掩码进行与运算，防止溢出
            if self.sequence == 0:  # 如果序列号归零
                timestamp = self.wait_next_millis(self.last_timestamp)  # 等待下一毫秒
        else:
            self.sequence = 0  # 时间戳变化，序列号重置为零

        self.last_timestamp = timestamp  # 更新上一次生成 ID 的时间戳

        # Generate Snowflake ID，生成 Snowflake ID
        _id = ((timestamp - self.tw_epoch) << (self.worker_id_bits + self.datacenter_id_bits)) | (
                self.datacenter_id << self.worker_id_bits) | self.worker_id << self.sequence_bits | self.sequence  # 使用时间戳、数据中心 ID、工作机器 ID 和序列号生成 ID
        return f"{_id:016d}"  # 返回 64 位长整型 ID 的字符串表示，补齐到16位长度

    def wait_next_millis(self, last_timestamp):
        timestamp = self.current_timestamp()  # 获取当前时间戳
        while timestamp <= last_timestamp:  # 循环直到获取到下一毫秒的时间戳
            timestamp = self.current_timestamp()
        return timestamp  # 返回下一毫秒的时间戳


if __name__ == '__main__':
    db2model()
