import cv2
import os
import random

def get_image():
    base = os.path.join(os.path.dirname(__file__), 'images')
    filename = os.path.join(base, random.choice(os.listdir(base)))
    return cv2.imread(filename)