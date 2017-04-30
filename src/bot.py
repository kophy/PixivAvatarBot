#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import random
import pickle
import os
import sys

from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
import pixivpy3
import redis

import avatar
import download
from text import *

"""
日志配置部分
"""
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO);
logger = logging.getLogger(__name__);

"""
Redis配置部分
"""
redis_server = redis.Redis(host = 'localhost', port = 6379,db = 0);
expire_time = 60;

def start(bot, update):
    update.message.reply_text(START_TEXT);

def help(bot, update):
    update.message.reply_text(HELP_TEXT);

"""
头像相关部分
"""

# 从日榜随机选择图片，使用redis缓存
def get_illust_from_ranking():
    illust = None;
    illust_id = redis_server.srandmember("illust_ids");
    illust_pkl = redis_server.hget("illust_id2pkl", illust_id);
    if illust_pkl == None:  # redis过期
        api = pixivpy3.AppPixivAPI();
        illusts = api.illust_ranking("day_male").illusts;
        for ist in illusts:
            redis_server.sadd("illust_ids", ist.id);
            redis_server.hset("illust_id2pkl", ist.id, pickle.dumps(ist));
            redis_server.expire("illust_ids", expire_time);
            redis_server.expire("illust_id2pkl", expire_time);
        illust = illusts[random.randint(0, len(illusts) - 1)];
        # print "redis failure";
    else:
        illust = pickle.loads(illust_pkl);
        # print "redis success";
    return illust;

# 从日榜图片中截取头像
def rank(bot, update):
    illust = get_illust_from_ranking();
    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii");
    if not download.download_image(url, "data", filename):
        update.message.reply_text(FAIL_DOWNLOAD_TEXT);
        return;
    if avatar.generate_avatar("data", filename):
        with open(os.path.join("data", "avatar_" + filename), "rb") as f:
            update.message.reply_photo(f);
            update.message.reply_text("pixiv id = %s" % str(illust.id))
    else:
        update.message.reply_text(NO_AVATAR_TEXT);
    os.remove(os.path.join("data", filename));

# TODO
def search(bot, update):
    pass;

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error));

"""
bot的主函数
"""
def main():
    cf = ConfigParser.ConfigParser();
    cf.read("pab.conf");
    token = cf.get("BOT", "TOKEN");

    updater = Updater(token);
    dp = updater.dispatcher;

    dp.add_handler(CommandHandler("start", start));
    dp.add_handler(CommandHandler("help", help));
    dp.add_handler(CommandHandler("rank", rank))
    dp.add_error_handler(error);

    updater.start_polling();
    updater.idle();

if __name__ == '__main__':
    main();
