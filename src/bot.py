#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import random
import pickle
import os, sys
import re

from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
import pixivpy3
import redis

from avatar import generate_avatar
from download import download_image
from config import *

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO);
logger = logging.getLogger(__name__);

redis_server = redis.Redis(host = 'localhost', port = 6379,db = 0);

"""
头像处理函数
"""

def get_top_K_illust(K):
    api = pixivpy3.AppPixivAPI();
    json_result = api.illust_ranking("day_male");
    illusts = json_result.illusts;
    while len(illusts) < K:
        next_qs = api.parse_qs(json_result.next_url);
        json_result = api.illust_ranking(**next_qs);
        illusts += json_result.illusts;
    return illusts[:min(K, len(illusts))];

# 从日榜随机选择图片，使用redis缓存
def get_illust_from_ranking():
    illust = None;
    illust_id = redis_server.srandmember(RANK_ID_SET);
    illust_pkl = redis_server.hget(RANK_ID_PKL_MAP, illust_id);
    if illust_pkl == None:  # 从缓存获取失败
        illusts = get_top_K_illust(LOWEST_RANK);
        for ist in illusts:
            redis_server.sadd(RANK_ID_SET, ist.id);
            redis_server.hset(RANK_ID_PKL_MAP, ist.id, pickle.dumps(ist));
        redis_server.expire(RANK_ID_SET, RANK_EXPIRE_TIME);
        redis_server.expire(RANK_ID_PKL_MAP, RANK_EXPIRE_TIME);
        illust = illusts[random.randint(0, len(illusts) - 1)];
        # print "redis failure";
    else:
        illust = pickle.loads(illust_pkl);
        # print "redis success";
    return illust;

# 检测这种头像是否已经存在
def find_cache(avatar_filename):
    if redis_server.lrem(CACHE_FILE_LIST, avatar_filename) > 0:
        add_cache(avatar_filename);
        return True;
    return False;

# 记录生成的头像，维持cache总数
def add_cache(avatar_filename):
    if redis_server.llen(CACHE_FILE_LIST) > MAX_CACHE_FILE_NUM:
        for i in range(PER_ERASE_FILE_NUM):
            temp = redis_server.rpop(CACHE_FILE_LIST);
            os.remove(os.path.join(CACHE_DIR, temp));
    redis_server.lpush(CACHE_FILE_LIST, avatar_filename);

# 从cache中随机获取头像文件
def get_random_from_cache():
    L = redis_server.llen(CACHE_FILE_LIST);
    if L > 0:
        return redis_server.lindex(CACHE_FILE_LIST, random.randint(0, L - 1));
    return None;

"""
bot handler函数
"""
def start(bot, update):
    update.message.reply_text(START_TEXT);

def help(bot, update):
    update.message.reply_text(HELP_TEXT);

# 从日榜图片中获取头像
def rank(bot, update):
    illust = get_illust_from_ranking();
    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii");
    avatar_filename = "avatar_" + filename;

    # cache中没有该头像文件
    if not find_cache(avatar_filename):
        # 下载文件 + 提取头像都成功
        if download_image(url, CACHE_DIR, filename) and generate_avatar(CACHE_DIR, filename):
            add_cache(avatar_filename);
        # 从目前缓存的头像中随机取, TODO：存在冷启动问题
        else:
            avatar_filename = get_random_from_cache();
            if avatar_filename == None:
                update.message.reply_text(NO_AVATAR_TEXT);
                return;

    with open(os.path.join(CACHE_DIR, avatar_filename), "rb") as f:
        update.message.reply_photo(f);
        pid = filter(str.isdigit, avatar_filename);
        update.message.reply_text("pixiv id = %s" % str(pid));

# TODO
def search(bot, update):
    update.message.reply_text("目前还不支持");

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error));

if __name__ == '__main__':
    cf = ConfigParser.ConfigParser();
    cf.read("token.conf");
    token = cf.get("BOT", "TOKEN");

    updater = Updater(token);
    dp = updater.dispatcher;

    dp.add_handler(CommandHandler("start", start));
    dp.add_handler(CommandHandler("help", help));
    dp.add_handler(CommandHandler("rank", rank));
    dp.add_handler(CommandHandler("search", search));
    dp.add_error_handler(error);

    updater.start_polling();
    updater.idle();
