#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy
from PIL import Image
import os

detector = cv2. CascadeClassifier("lib/lbpcascade_animeface.xml");
face_width = 50;

def detect_faces(image):
    """
    检测图片中是否有人脸
    :param image: 待检测图片(opencv格式)
    :return: 所有人脸窗口坐标的list
    """
    gray = None;
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    except:
        gray = image;
    gray = cv2.equalizeHist(gray);
    faces = detector.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 5, minSize = (face_width, face_width));
    return faces;

def crop_avatar(image):
    """
    从图片则截取头像
    :param image: 待截取图片(opencv格式)
    :return: 截取的头像图片(opencv格式)，不存在则返回None
    """
    faces = detect_faces(image);
    if len(faces) == 0:
        return None;
    areas = [w * h for (x, y, w, h) in faces];

    # 选择最大的人脸
    idx = areas.index(max(areas));
    x, y, w, h = faces[idx];
    width = max(w, h);

    # round up，截取的窗口要在原图片内
    l, r = max(int(y - 0.3 * width), 0), min(int(y + 1.3 * width), image.shape[0]);
    d, u = max(int(x - 0.3 * width), 0), min(int(x + 1.3 * width), image.shape[1]);
    return image[l:r, d:u];

def generate_avatar(dir, filename):
    """
    生成头像图片文件，保存为dir/avatar_filename
    :return: 表示是否生成头像的bool值
    """
    pil_image = numpy.array(Image.open(os.path.join(dir, filename)));
    image = None;
    try:
        image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR);
    except:
        image = numpy.array(pil_image);
    avatar = crop_avatar(image);
    if avatar is None:
        return False;
    else:
        cv2.imwrite(os.path.join(dir, "avatar_" + filename), avatar);
        return True;

if __name__ == "__main__":
    flag = get_avatar("data", "1.png");
    print flag;
