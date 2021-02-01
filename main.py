import cProfile

from files import *
from objects import *
from video import *

def showImage(image, windowName):
	cv2.namedWindow(windowName)
	cv2.imshow(windowName, image)

def test():
	dataset_root_folder = '../aff-wild2'
	files = getFiles(dataset_root_folder)

	aff_wild_videos = Objects(files, ['mp4', 'avi'])
	aff_wild_videos_iter = iter(aff_wild_videos)

	pairs = []
	objects = []
	for object in aff_wild_videos_iter:
		annotations = getAnnotations(object, files)
		pairs.append({
			'object': object,
			'annotation': annotation
		})
		if len(pairs) % 10000 == 0:
			print(len(pairs))
		# objects.append(object)
		# data = readObject(object)
		# showImage(data, 'data')
		# cv2.waitKey(0)
	print(len(objects))

# test()
# cProfile.run('test()')

import cv2
import numpy as np
from scipy.spatial import distance

def resize(image, scale = 0.5):
	width = int(image.shape[1] * scale)
	height = int(image.shape[0] * scale)
	return cv2.resize(image, (width, height))

import math

def getHog(image):
	cells_by_side = 16
	# print('image size:', image.shape)
	cell_size = (math.floor(image.shape[0] / cells_by_side), math.floor(image.shape[1] / cells_by_side))  # h x w in pixels
	block_size = (1, 1)  # h x w in cells
	nbins = 9  # number of orientation bins

	# winSize is the size of the image cropped to an multiple of the cell size
	# cell_size is the size of the cells of the img patch over which to calculate the histograms
	# block_size is the number of cells which fit in the patch
	_winSize=(cells_by_side * cell_size[1], cells_by_side * cell_size[0])
	image = image[0:_winSize[1], 0:_winSize[0]]
	# print('new image size:', image.shape, _winSize[0], _winSize[1])
	# print('_winSize:', _winSize, _winSize[0] / cell_size[1], _winSize[1] / cell_size[0])
	_blockSize=(block_size[1] * cell_size[1],
				block_size[0] * cell_size[0])
	_blockStride=(cell_size[1], cell_size[0])
	_cellSize=(cell_size[1], cell_size[0])
	# print('_cell_size:', _cellSize)
	_nbins=nbins
	hog = cv2.HOGDescriptor(_winSize=_winSize,
	                        _blockSize=_blockSize,
	                        _blockStride=_blockStride,
	                        _cellSize=_cellSize,
	                        _nbins=_nbins)
	result = hog.compute(image).T[0]
	# print('hog size:', result.shape)
	return result

def getHogMatrix(images):
	return np.array([getHog(image) for image in images])

videos = map(getVideo, ['../aff-wild2/expr/videos/validation_set/118-30-640x480.mp4'])
frames = map(getCurrentFrame, videos)
hogMatrix = getHogMatrix(frames)
for v in hogMatrix:
	print(v.shape)
	print(v[:18])
exit()

import cupy as cp
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed

from numba import jit

def distance_cosine(a, b, lib):
	numerator = lib.dot(a, b)
	a_norm = lib.sqrt(lib.sum(a ** 2))
	b_norm = lib.sqrt(lib.sum(b ** 2))
	denominator = a_norm * b_norm
	result = 1 - numerator / denominator
	return result

@jit(nopython=True)
def cosine_similarity_numba(u:np.ndarray, v:np.ndarray):
    assert(u.shape[0] == v.shape[0])
    uv = 0
    uu = 0
    vv = 0
    for i in range(u.shape[0]):
        uv += u[i]*v[i]
        uu += u[i]*u[i]
        vv += v[i]*v[i]
    cos_theta = 1
    if uu!=0 and vv!=0:
        cos_theta = uv/np.sqrt(uu*vv)
    return cos_theta

def distance_cosine_np(a, b):
	numerator = np.dot(a, b)
	a_norm = np.sqrt(np.sum(a ** 2))
	b_norm = np.sqrt(np.sum(b ** 2))
	denominator = a_norm * b_norm
	result = 1 - numerator / denominator
	return result

@timeit
def distance_cosine_for(A, B, f, lib):
	for i in range(A.shape[0]):
		a = A[i]
		b = B[i]
		f(a, b)

def generate(lib, size):
	return lib.array([lib.random.uniform(size = 2048) for i in range(size)]), lib.array([lib.random.uniform(size = 2048) for i in range(size)])

with cp.cuda.Device(0):
	for lib in ['np', 'cp']:
		print(lib)
		print('generating...')
		A, B = generate(lib, 512)
		print('calculating...')
		distance_cosine_for(A, B, distance_cosine, lib)
# A, B = generate(np, 512)
# distance_cosine_for(A, B, distance_cosine_np, 'np')
exit()

# optimized, complexity is n * (n-1) / 2
def getSimilaritiesMatrix(matrix):
	numberOfVectors = matrix.shape[0]
	result = np.zeros([numberOfVectors, numberOfVectors])
	for i in range(numberOfVectors):
		for j in range(i + 1, numberOfVectors):
			vector1 = matrix[i]
			vector2 = matrix[j]
			# print(vector1.shape, vector1)
			# print(vector2.shape, vector2)
			# exit()
			d = distance.cosine(vector1, vector2)
			result[i][j] = d
			result[j][i] = d
	return 1 - result

def getMetrics(similarities_matrix):
	return np.array([np.mean(similarities_matrix)])

dataset_root_folder = '../aff-wild2'
files = getFiles(dataset_root_folder)
print('loaded files')

aff_wild_videos = Objects(files, ['mp4', 'avi'])
aff_wild_videos_iter = iter(aff_wild_videos)
all_objects = [object for object in aff_wild_videos_iter]
print('loaded objects')

def getHogSimilaritiesMatrix(images):
	return getSimilaritiesMatrix(getHogMatrix(images))

def getMetricsDeltas(images1, images2):
	metrics1 = getMetrics(getHogSimilaritiesMatrix(images1))
	metrics2 = getMetrics(getHogSimilaritiesMatrix(images2))
	return metrics2 / metrics1

import random

def experiment(attempts = 1):
	results = np.empty([attempts])
	for i in range(attempts):
		objects = random.sample(all_objects, 100)
		# print(objects)
		images = list(map(readObject, objects))
		print('images:', [t for t in map(type, images)])
		resized_images = list(map(resize, images))
		results[i] = getMetricsDeltas(images, resized_images)
	return results

import os

def experiment1():
	processed = 0
	paths = {}
	shapes = {}
	for object in all_objects:
		path = os.path.normcase(object['dir'] + '/' + object['name'] + '.' + object['extension'])
		processed += 1
		if processed % 100000 == 0:
			print('processed', processed, 'images')
		if path in paths:
			continue
		paths[path] = True
		image = readObject(object)
		shape = str(image.shape)
		if shape in shapes:
			continue
		shapes[shape] = True
		hog = getHog(image)
		if hog.shape[0] != 2304:
			print(hog.shape, object)

cProfile.run('experiment()')