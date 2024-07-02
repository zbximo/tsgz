# -*- encoding: utf-8 -*-
# @ModuleName: Tools
# @Author: ximo
# @Time: 2024/5/9 11:12
import os
import random
import subprocess
from db.database import dbTools
import time
import threading


def db2model():
    db = dbTools()
    r = db.open_ssh()
    print(r)

    sqlacodegen_command = f"""
    /opt/anaconda3/envs/tsgz/bin/sqlacodegen mysql+pymysql://root:tsgz2024@0.0.0.0:{r[1]}/situation_system --tables data_add,data_event,data_news,data_person,data_similar,data_social_comment,data_social_post,data_task --outfile /mnt/data/users/xhd/tsgz/db/entity.py"""
    print(sqlacodegen_command)
    result = subprocess.run(sqlacodegen_command, shell=True)
    print(result.returncode)
    db.close_ssh()


def get_stopwords():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'baidu_stopwords.txt')

    with open(file_path, "r") as f:
        stop_words = f.read().splitlines()
    return stop_words


class SnowFlake(object):
    def __init__(self, worker_id=1, datacenter_id=1, sequence=0):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.tw_epoch = 1288834974657

        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.sequence_bits = 12
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        self.last_timestamp = -1

        if self.worker_id > self.max_worker_id or self.worker_id < 0:
            raise ValueError(f"Worker ID must be between 0 and {self.max_worker_id}")
        if self.datacenter_id > self.max_datacenter_id or self.datacenter_id < 0:
            raise ValueError(f"Datacenter ID must be between 0 and {self.max_datacenter_id}")

        self.lock = threading.Lock()  # Use a lock for thread safety

    @staticmethod
    def current_timestamp():
        return int(time.time() * 1000)

    def wait_next_millis(self, last_timestamp):
        timestamp = self.current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self.current_timestamp()
        return timestamp

    # def generate_(self):
    #     with self.lock:  # Ensure thread safety
    #         timestamp = self.current_timestamp()
    #         while True:
    #             if timestamp < self.last_timestamp:
    #                 continue
    #                 # raise ValueError("Clock moved backwards. Refusing to generate ID for {} milliseconds".format(
    #                 #     self.last_timestamp - timestamp))
    #
    #             if timestamp == self.last_timestamp:
    #                 self.sequence = (self.sequence + 1) & self.sequence_mask
    #                 if self.sequence == 0:
    #                     timestamp = self.wait_next_millis(self.last_timestamp)
    #             else:
    #                 self.sequence = 0
    #
    #             self.last_timestamp = timestamp
    #
    #             _id = ((timestamp - self.tw_epoch) << (self.worker_id_bits + self.datacenter_id_bits + self.sequence_bits)) | (
    #                     (self.datacenter_id << self.worker_id_bits) | self.worker_id << self.sequence_bits | self.sequence)
    #             return _id
    def generate(self):
        random_number = random.randint(100, 999)

        t = time.time()
        tt = int(round(t * 1000000))
        _id = int(f"{tt}{random_number}")
        return _id


if __name__ == '__main__':
    db2model()
