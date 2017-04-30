#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy
from PIL import Image

import os

from config import FACE_WIDTH

detector = cv2. CascadeClassifier("lib/lbpcascade_animeface.xml");

# 检测图片中是否有人脸
def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    gray = cv2.equalizeHist(gray);
    faces = detector.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 5, minSize = (FACE_WIDTH, FACE_WIDTH));
    return faces;

# 存在人脸则返回头像图片，否则None
def crop_avatar(image):
    faces = detect_faces(image);
    if len(faces) == 0:
        return None;
    areas = [w * h for (x, y, w, h) in faces];
    idx = areas.index(max(areas));  # 选择最大的人脸
    x, y, w, h = faces[idx];
    width = max(w, h);

    # round up
    l, r = max(int(y - 0.3 * width), 0), min(int(y + 1.3 * width), image.shape[0]);
    d, u = max(int(x - 0.3 * width), 0), min(int(x + 1.3 * width), image.shape[1]);

    cropped = image[l:r, d:u];
    return cropped;

# 生成头像图片文件，返回bool值表示生成是否成功
# 默认删除源文件
def generate_avatar(dir, filename, remove = True):
    pil_image = numpy.array(Image.open(os.path.join(dir, filename)));
    if remove:
        os.remove(os.path.join(dir, filename));
    image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR);
    avatar = crop_avatar(image);
    if avatar is None:
        return False;
    cv2.imwrite(os.path.join(dir, "avatar_" + filename), avatar);
    return True;

if __name__ == "__main__":
    flag = get_avatar("data", "1.png");
    print flag;
