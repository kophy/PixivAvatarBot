#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import sys

cascade = cv2. CascadeClassifier("lib/lbpcascade_animeface.xml");
image = cv2.imread("data/4.jpg");
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
gray = cv2.equalizeHist(gray);
faces = cascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 5, minSize = (25, 25));

areas = [w * h for (x, y, w, h) in faces];
print areas.index(max(areas));

for (x, y, w, h) in faces:
    cropped = image[int(y - 0.3 * h):int(y + 1.3 * h), int(x - 0.3 * w):int(x + 1.3 * w)]
    cv2.rectangle(image, (int(x - 0.25 * w), int(y - 0.25 * h)), (int(x + 1.25 * w), int(y + 1.25 * h)), (0, 0, 255), 2)

cv2.imshow("AnimeFaceDetect", image)
cv2.waitKey(0)
cv2.imwrite("out.png", cropped)

def crop_avatar(filename, scaling = 0.25):
    pass;
