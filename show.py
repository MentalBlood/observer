import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, floor, ceil
from objects import readObject
from classes import getShuffledPairsFromClass
from multiprocessing.pool import ThreadPool

def showImage(image, windowName):
	cv2.namedWindow(windowName)
	cv2.imshow(windowName, image)

def resize(image, scale = 0.5):
	width = int(image.shape[1] * scale)
	height = int(image.shape[0] * scale)
	return cv2.resize(image, (width, height))

def showPairsImages(pairs, rows = None, columns = None):
	sqrt_len = sqrt(len(pairs))
	if (rows == None) or (columns == None):
		columns = 10
		rows = ceil(len(pairs) / columns)
	fig = plt.figure(figsize=(3 * columns, 3 * rows))
	# figManager = plt.get_current_fig_manager()
	# figManager.full_screen_toggle()
	# plt.subplots_adjust(wspace = 0, hspace = 0.1)
	plt.tight_layout(pad = 0, h_pad = 4, w_pad = 4)
	def getImage(p):
		image = readObject(p[1]['object'])
		if image is not None:
			return (cv2.cvtColor(readObject(p[1]['object']), cv2.COLOR_BGR2RGB), p[0])
	for image_and_index in ThreadPool(16).imap_unordered(getImage, enumerate(pairs)):
		if image_and_index == None:
			continue
		fig.add_subplot(rows, columns, image_and_index[1] + 1)
		plt.imshow(image_and_index[0])
	plt.show()

def showFromClass(pairs, class_name, number_of_images = 12, rows = None, columns = None):
	shuffled_pairs = getShuffledPairsFromClass(pairs, class_name)
	shuffled_pairs.setMax(number_of_images)
	showPairsImages(shuffled_pairs, rows, columns)

def showContinuously(pairs, number_of_images_on_screen = 4):
	while True:
		for i in range(ceil(len(pairs) / number_of_images_on_screen)):
			a = number_of_images_on_screen * i
			b = min(a + number_of_images_on_screen, len(pairs))
			showPairsImages(pairs[a:b])

def showFromClassContinuously(pairs, class_name, number_of_images_on_screen = 4):
	shuffled_pairs = getShuffledPairsFromClass(pairs, class_name)
	showContinuously(shuffled_pairs, number_of_images_on_screen)