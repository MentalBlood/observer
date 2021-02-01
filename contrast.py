import numpy as np
# import mxnet as mx
import cv2

# ctx = mx.gpu()

np_weights = np.array([0.3, 0.59, 0.11]) / 256
def getGrayscaleImage(image):
	return np.dot(image[...,:3], np_weights)

def getImageContrast(image):
	intensities = getGrayscaleImage(image)
	intensitiesVector = np.reshape(intensities, -1)
	intensitiesVectorSize = intensitiesVector.shape[0]
	meanIntensity = np.mean(intensitiesVector)
	return np.mean((intensitiesVector - meanIntensity) ** 2)

def getScatter(imagesContrasts):
	mean = np.mean(imagesContrasts)
	return np.mean((intensitiesVector - meanIntensity) ** 2)



# mx_weights = mx.nd.array([0.3, 0.59, 0.11], ctx=ctx) / 256
# def mx_getGrayscaleImage(image):
# 	mx_image = mx.nd.array(image, ctx=ctx)
# 	return mx.nd.dot(mx_image, mx_weights)

# def mx_getImageContrast(image):
# 	intensities = mx_getGrayscaleImage(image)
# 	intensitiesVector = intensities.reshape(-1)
# 	meanIntensity = mx.nd.mean(intensitiesVector)
# 	return mx.nd.mean((intensitiesVector - meanIntensity) ** 2)

# def mx_getScatter(imagesContrasts):
# 	mean = np.mean(imagesContrasts)
# 	return np.mean((intensitiesVector - meanIntensity) ** 2)