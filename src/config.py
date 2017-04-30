#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
头像配置部分
"""
LOWEST_RANK = 100;  # 排名范围
FACE_WIDTH = 30;    # 头像检测时窗口宽度

"""
Redis配置部分
"""
RANK_ID_SET = "rank_id_set";
RANK_ID_PKL_MAP = "rank_id2pkl_map";
RANK_EXPIRE_TIME = 60;

CACHE_FILE_LIST = "cache_file_list";
MAX_CACHE_FILE_NUM = 100;
PER_ERASE_FILE_NUM = 20;

"""
提示语部分
"""
START_TEXT = (
    "欢迎使用PixivAvatarBot\n"
    "使用 /help 了解命令"
);

HELP_TEXT = (
    "/rank - pixiv日榜随机图片\n"
    "/search - 关键词搜索图片\n"
);

FAIL_DOWNLOAD_TEXT = (
    "下载失败了我也很绝望呀\n"
    "请稍后再试吧"
);

NO_AVATAR_TEXT = (
    "图片学姐了我也很绝望呀\n"
    "请再试一次吧"
);
