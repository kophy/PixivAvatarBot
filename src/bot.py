#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import os, sys

from telegram.ext import *

from avatar import generate_avatar
from download import download_image
from file_cache import find_cache, add_cache, get_random_from_cache
from illust_info import get_illust_from_ranking, get_illust_from_keywords, blacklist_illust_in_ranking
from config import *

logging.basicConfig(format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level = logging.INFO);
logger = logging.getLogger(__name__);

KEYWORD = 1;

def start(bot, update):
    """
    处理 /start 命令的函数
    """
    update.message.reply_text(START_TEXT);

def help(bot, update):
    """
    处理 /help 命令的函数
    """
    update.message.reply_text(HELP_TEXT);

def rank(bot, update):
    """
    处理 /rank 命令的函数
    工作流程:
        1. 从日榜中随机获取一张图片的信息
        2. 检查对应头像是否在文件缓存中，有转7
        3. 下载图片，尝试截取头像，失败转5
        4. 把新头像加入文件缓存，转7
        5. 拉黑失败的图片信息，从文件缓存中随机获取一张头像，成功转7
        6. 回复失败，退出
        7. 回复图片，退出
    """
    illust = get_illust_from_ranking();
    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii"); # 否则redis缓存时有编码问题
    filepath = os.path.join(CACHE_DIR, filename);
    avatar_filepath = os.path.join(CACHE_DIR, "avatar_" + filename);

    success = False;    # 是否回复图片

    if not find_cache(avatar_filepath): # cache中没有该头像文件
        success = download_image(url, CACHE_DIR, filename) and generate_avatar(CACHE_DIR, filename);
        if os.path.exists(filepath): os.remove(filepath);

        # 下载文件和提取头像都成功
        if success:
            add_cache(avatar_filepath); # 把新头像加入缓存

        # 从缓存中随机取头像
        else:
            blacklist_illust_in_ranking(illust.id); # 把失败的尝试拉入黑名单
            avatar_filepath = get_random_from_cache();

            # 没有缓存头像，才会真正失败
            success = (avatar_filepath is not None);
    else:
        success = True;

    if success:
        with open(avatar_filepath, "rb") as f:
            update.message.reply_photo(f);
            pid = filter(str.isdigit, avatar_filepath); # 从文件名提取pixiv id
            update.message.reply_text("pixiv id = %s" % str(pid));
    else:
        update.message.reply_text(NO_AVATAR_TEXT);

def search_entry(bot, update):
    """
    处理 /search 命令的函数，关键词搜索的入口点
    """
    update.message.reply_text(ASK_KEYWORD_TEXT);
    return KEYWORD;

def search_impl(bot, update):
    """
    处理 /search 命令的函数，关键词搜索的实现
    工作流程:
        1. 根据关键词随机获取一张图片的信息
        2. 检查对应头像是否在文件缓存中，有转6
        3. 下载图片，尝试截取头像，失败转5
        4. 把新头像加入文件缓存，转6
        5. 回复失败，退出
        6. 回复图片，退出
    """
    keywords = update.message.text + " 100";    # 通过人气保证图片质量
    illust = get_illust_from_keywords(keywords);

    # 关键词错误等原因，没有符合条件的图片
    if illust is None:
        update.message.reply_text(ERROR_KEYWORD_TEXT);
        return ConversationHandler.END;

    url = illust.image_urls.large;
    filename = (str(illust.id) + "." + url.split(".")[-1]).encode("ascii"); # 否则redis缓存时有编码问题
    filepath = os.path.join(CACHE_DIR, filename);
    avatar_filepath = os.path.join(CACHE_DIR, "avatar_" + filename);

    success = False;        # 是否回复图片

    if not find_cache(avatar_filepath): # cache中没有该头像文件
        success = download_image(url, CACHE_DIR, filename) and generate_avatar(CACHE_DIR, filename);
        if os.path.exists(filepath): os.remove(filepath);

        # 下载文件和提取头像都成功
        if success:
            add_cache(avatar_filepath); # 把新头像加入缓存
    else:
        success = True;

    if success:
        with open(avatar_filepath, "rb") as f:
            update.message.reply_photo(f);
            pid = filter(str.isdigit, avatar_filepath); # 从文件名提取pixiv id
            update.message.reply_text("pixiv id = %s" % str(pid));
    else:
        update.message.reply_text(NO_AVATAR_TEXT);
    return ConversationHandler.END;

def cancel(bot, update):
    return ConversationHandler.END;

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error));

if __name__ == "__main__":
    cf = ConfigParser.ConfigParser();
    cf.read("token.conf");
    token = cf.get("BOT", "TOKEN");

    updater = Updater(token);
    dp = updater.dispatcher;

    dp.add_handler(CommandHandler("start", start));
    dp.add_handler(CommandHandler("help", help));
    dp.add_handler(CommandHandler("rank", rank));

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler("search", search_entry)],
        states = {
            KEYWORD: [MessageHandler(Filters.text, search_impl)]
        },
        fallbacks = [CommandHandler("cancel", cancel)]
    );
    dp.add_handler(conv_handler);

    dp.add_error_handler(error);

    updater.start_polling();
    updater.idle();
