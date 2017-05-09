#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pixivpy3
import pickle
from random import randint

from config import rs

RANK_ID_SET = "rank_id_set";            # redis中缓存日榜pid的集合
RANK_PKL_MAP = "rank_id2pkl_map";       # redis中缓存日榜pid->图片信息的哈希表
RANK_EXPIRE_TIME = 300;                 # 日榜信息过期时间(单位：秒)
RANK_QUERY_NUM = 100;                   # 每次从日榜获取的图片信息数

def get_top_illusts(K):
    """
    获取日榜中前K名的信息
    :param K: 要获取的图片信息数量
    :return: 日榜中前K张图片的信息list
    """
    api = pixivpy3.AppPixivAPI();
    json_result = api.illust_ranking("day_male");
    illusts = json_result.illusts;
    while len(illusts) < K:
        next_qs = api.parse_qs(json_result.next_url);
        json_result = api.illust_ranking(**next_qs);
        illusts += json_result.illusts;
    return illusts[:min(K, len(illusts))];

# TODO: 优化等待时间
def get_illust_from_ranking():
    """
    从日榜随机获取图片
    :return: 一张图片的信息(可能为None)
    """
    illust = None;
    illust_id = rs.srandmember(RANK_ID_SET);
    illust_pkl = rs.hget(RANK_PKL_MAP, illust_id);

    # 从缓存获取图片信息失败
    if illust_pkl == None:
        # 更新排名信息
        illusts = get_top_illusts(RANK_QUERY_NUM);
        for i in range(len(illusts)):
            rs.sadd(RANK_ID_SET, illusts[i].id);
            rs.hset(RANK_PKL_MAP, illusts[i].id, pickle.dumps(illusts[i]));
        rs.expire(RANK_ID_SET, RANK_EXPIRE_TIME);
        rs.expire(RANK_PKL_MAP, RANK_EXPIRE_TIME);

        illust = illusts[randint(0, len(illusts) - 1)];
        # print "redis failure";
    else:
        illust = pickle.loads(illust_pkl);
        # print "redis success";
    return illust;

def get_illust_from_keywords(keywords):
    """
    根据关键词随机获取一张图片的信息
    :param keywords: 关键词（字符串）
    :return: 一张图片的信息(可能为None)
    """
    illust = None;
    api = pixivpy3.AppPixivAPI();
    json_result = api.search_illust(keywords, search_target = "partial_match_for_tags");
    illusts = json_result.illusts;
    if len(illusts) > 0:
        illust = illusts[randint(0, len(illusts) - 1)];
    return illust;

def blacklist_illust_in_ranking(illust_id):
    """
    "拉黑"日榜中没有人脸的图片
    :param illust_id: 要拉黑图片的pixiv id
    """
    rs.srem(RANK_ID_SET, illust_id);

if __name__ == "__main__":
    print get_illust_from_ranking();
    print get_illust_from_ranking();
