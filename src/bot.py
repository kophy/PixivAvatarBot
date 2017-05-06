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
from file_cache import find_cache, add_cache, get_random_from_cache
from config import *

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO);
logger = logging.getLogger(__name__);

redis_server = redis.Redis(host = 'localhost', port = 6379,db = 0);

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

"""
bot handler函数
"""
def start(bot, update):
    update.message.reply_text(START_TEXT);

def help(bot, update):
    update.message.reply_text(HELP_TEXT);

def rank(bot, update):
    """
    从日榜图片中获取头像
    """
    illust = get_illust_from_ranking();
    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii");
    filepath = os.path.join(CACHE_DIR, filename);
    avatar_filepath = os.path.join(CACHE_DIR, "avatar_" + filename);

    # cache中没有该头像文件
    if not find_cache(avatar_filepath):
        success = download_image(url, CACHE_DIR, filename) and generate_avatar(CACHE_DIR, filename);
        if os.path.exists(filepath):
            os.remove(filepath);
        # 下载文件 + 提取头像都成功
        if success:
            add_cache(avatar_filepath);
        # 从目前缓存的头像中随机取, TODO：存在冷启动问题
        else:
            avatar_filepath = get_random_from_cache();
            if avatar_filepath == None:
                update.message.reply_text(NO_AVATAR_TEXT);
                return;

    with open(avatar_filepath, "rb") as f:
        update.message.reply_photo(f);
        pid = filter(str.isdigit, avatar_filepath); # 从文件名提取pid
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
