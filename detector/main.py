from utils import get_image
from detector import Detector

detector = Detector('/Users/caxapok/Desktop/GrainFocus/best.pt')
detector.process(get_image())
