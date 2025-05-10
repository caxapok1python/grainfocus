from utils import get_image
from detector import Detector

detector = Detector('./yolo11x.pt')

while True:
    detector.process(get_image())
