#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os
import sys
from random import randint
import time

def download_image(url, dir, filename):
    """
    从P站下载图片
    :return: 表示下载是否成功的bool值
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) \
                  AppleWebKit/537.36 (KHTML, like Gecko) \
                  Chrome/44.0.2403.155 Safari/537.36";
    headers = {"Referer": "http://www.pixiv.net", "User-Agent": user_agent};
    for i in range(3):
        try:
            response = requests.get(url, headers = headers, timeout = 10);
            with open(os.path.join(dir, filename), "wb") as f:
                f.write(response.content);
            return True;
        except requests.exceptions.RequestException:
            time.sleep(randint(5, 10));
    return False;

if __name__ == "__main__":
    flag = download_image("https://i.pximg.net/img-master/img/2017/04/27/00/04/27/62593166_p0_master1200.jpg", "data", "1.png");
    print flag;
