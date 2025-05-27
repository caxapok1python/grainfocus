from pprint import pprint
import requests

import numpy as np
from ultralytics import YOLO
import cv2
import os




class Detector:
    allowed_classes = {0, 1}
    dirname = os.path.dirname(__file__)
    
    def __init__(self, weights='yolo11x.pt'):
        self.model = YOLO(weights)

    def process(self, frame):
        frame = cv2.resize(frame, (640, 640))
        res = self.model(frame)
        annotated = self.draw_boxes(frame, res)
        cv2.imwrite('../web/share/detection/annotated.png', annotated)
        cv2.imwrite('../web/share/detection/image.png', frame)
        # 3) Считаем объекты по классам
        cls_ids = res[0].boxes.cls.cpu().numpy().astype(int)
        # np.bincount вернёт array длиной max(cls_ids)+1
        counts = np.bincount(cls_ids, minlength=3)
        # Сортируем по заранее определённому порядку классов: [broken, weed]
        broken_cnt, weed_cnt = counts[0], counts[1]
        total = sum(counts)

        broken_pct = round(broken_cnt / total * 100, 1)
        weed_pct = round(weed_cnt / total * 100, 1)

        # 4) Пишем текстовый файл
        data_line = f"{broken_cnt},{weed_cnt},{total}"
        with open('../web/share/detection/classes.txt', 'w') as f:
            f.write(data_line)

        pprint(data_line)

        payload = {"weed_pct": weed_pct, "broken_pct": broken_pct}
        try:
            resp = requests.post(
                "http://localhost:8080/api/session/latest/add",
                json=payload,
                timeout=2
            )
            resp.raise_for_status()
        except Exception as e:
            print("Failed to send reading:", e)

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


