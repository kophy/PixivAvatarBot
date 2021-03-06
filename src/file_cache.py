#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import os
from random import randint

from config import rs

"""
可配置参数
"""
CACHE_NAME = "cached_filepath_list";    # redis中保存缓存文件信息的链表
MAX_CACHE_NUM = 200;                    # 最大缓存文件数
PER_ERASE_NUM = 20;                     # 缓存满时删除文件数

def find_cache(filepath):
    """
    检测文件是否已经缓存
    :param filepath: 文件路径
    :return: 表示是否存在的bool值
    """
    if rs.lrem(CACHE_NAME, filepath) > 0:
        add_cache(filepath);
        return True;
    return False;

def add_cache(filepath):
    """
    添加文件到缓存
    :param filepath: 文件路径
    """
    if rs.llen(CACHE_NAME) > MAX_CACHE_NUM:
        for i in range(PER_ERASE_NUM):
            temp = rs.rpop(CACHE_NAME);
            os.remove(temp);
    rs.lpush(CACHE_NAME, filepath);

def get_random_from_cache():
    """
    从缓存中随机获取文件
    :return: 缓存中随机文件路径，缓存空则返回None
    """
    L = rs.llen(CACHE_NAME);
    if L > 0:
        return rs.lindex(CACHE_NAME, randint(0, L - 1));
    return None;
