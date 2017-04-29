#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import random
import os
import sys

from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
import pixivpy3

import avatar
import download
from text import *

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level = logging.INFO);
logger = logging.getLogger(__name__);

def start(bot, update):
    update.message.reply_text(START_TEXT);

def help(bot, update):
    update.message.reply_text(HELP_TEXT);

"""
头像相关部分
"""

# TODO: 增加cache
def get_illust(method):
    api = pixivpy3.AppPixivAPI();
    illust = None;
    if method == "rank":
        illusts = api.illust_ranking("day_male").illusts;
        illust = illusts[random.randint(0, len(illusts) - 1)];
    return illust;

# TODO: 图片信息（链接，PID等）
def rank(bot, update):
    illust = get_illust("rank");
    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii");
    if not download.download_image(url, "data", filename):
        update.message.reply_text(FAIL_DOWNLOAD_TEXT);
        return;
    if avatar.get_avatar("data", filename):
        with open(os.path.join("data", "avatar" + filename), "rb") as f:
            update.message.reply_photo(f);
    else:
        update.message.reply_text(NO_AVATAR_TEXT);
    os.remove(os.path.join("data", filename));

# TODO
def search(bot, update):
    pass;

# TODO
def upload(bot, update):
    pass;


def cancel(bot, update):
    pass;

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error));

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
