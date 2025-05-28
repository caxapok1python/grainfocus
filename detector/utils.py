import cv2
import os
import random

def get_image():
    base = "images"
    filename = os.path.join(base, random.choice(os.listdir(base)))
    return cv2.imread(filename)