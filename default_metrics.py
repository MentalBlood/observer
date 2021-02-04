from hog import getHog
from contrast import getImageContrast
import cv2

def getHistogram(image):
	grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	return cv2.calcHist([grayscale], [0], None, [256], [0,256]).reshape(-1)

metrics = {
	'hog': getHog,
	'contrast': getImageContrast,
	'height': lambda i: i.shape[0],
	'width': lambda i: i.shape[1],
	'width_height_ratio': lambda i: i.shape[1] / i.shape[0],
	'histogram': getHistogram
}