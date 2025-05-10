from pprint import pprint

import numpy as np
from ultralytics import YOLO
import cv2
import os


class Detector:
    allowed_classes = {0, 1}
    dirname = os.path.dirname(__file__)
    def __init__(self, weights='yolo11x.pt'):
        self.model = YOLO(weights)

    def process(self, img):
        res = self.model(img)
        annotated = self.draw_boxes(img, res)
        cv2.imwrite('../web/share/detection/annotated.png', annotated)
        cv2.imwrite('../web/share/detection/image.png', img)
        cls_ids = res[0].boxes.cls.cpu().numpy().astype(int)
        cls = np.bincount(cls_ids)
        data =f"{cls[0]},{cls[1]},{cls[2]}"
        with open('../web/share/detection/classes.txt', 'w') as f:
            f.write(data)
        pprint(data)

    def draw_boxes(self, img, results):
        img = img.copy()
        r = results[0]

        # r.boxes.xyxy — N×4, r.boxes.cls — N элементов
        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()

        # Рисуем только для нужных классов
        for box, cls in zip(boxes, classes):
            if int(cls) in self.allowed_classes:
                x1, y1, x2, y2 = map(int, box)
                color = (81, 202, 227) if cls == 1 else (117, 119, 214)
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        return img


