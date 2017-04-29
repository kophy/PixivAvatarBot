#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urllib2

import os
import sys

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) \
              AppleWebKit/537.36 (KHTML, like Gecko) \
              Chrome/44.0.2403.155 Safari/537.36";
HEADERS = {"Referer": "http://www.pixiv.net", "User-Agent": USER_AGENT};
MAX_RETRY = 5;

# 从P站下载图片，返回bool值表示下载是否成功
def download_image(url, dir, filename):
    for i in range(MAX_RETRY):
        try:
            response = requests.get(url, headers = HEADERS, timeout = 10);
            with open(os.path.join(dir, filename), 'wb') as f:
                f.write(response.content);
            return True;
        except requests.exceptions.RequestException:
            time.sleep(random.randint(5, 10));
    return False;

if __name__ == "__main__":
    flag = download_image("https://i.pximg.net/img-master/img/2017/04/27/00/04/27/62593166_p0_master1200.jpg", "data", "1.png");
    print flag;
