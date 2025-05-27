import cv2
from utils import get_image
from detector import Detector

detector = Detector('./yolo11x.pt')

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    detector.process(frame)
    cv2.waitKey(1)

cap.release()