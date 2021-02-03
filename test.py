from sklearn.cluster import KMeans
import numpy as np
from pairs import Pairs
from filters import getPairsMetrics, getPairsMetricsWithPairs
from dataset_specific_api import getDatasetSpecificApi
import cProfile
from objects import getObjectPath
import cv2
from matplotlib import pyplot as plt

dataset_name = 'FMDDS_resized'
clusters_number = 2
dataset_dir = 'pairs_' + dataset_name + '_new'
dataset_specific_api = getDatasetSpecificApi('FMDDS')
pairs = Pairs(dataset_dir, get_classes_function=dataset_specific_api.getClasses)
pairs.setReturnNames(True)
pairs.filterBy({'__class__': ['face_no_mask']})

class OnFlowMetric():
	def __init__(self, name, init_value, refresh_function, get_function):
		self.name = name
		self.init_value = init_value
		self.refresh_function = refresh_function
		self.get_function = get_function

	def init(self):
		self.current_value = self.init_value

	def refresh(self, new_data, log=True):
		if self.refresh_function.__code__.co_argcount > 2:
			self.current_value = self.refresh_function(self.current_value, new_data, log=log)
		else:
			self.current_value = self.refresh_function(self.current_value, new_data)

	def getValue(self):
		return self.get_function(self.current_value)

	def getInfo(self):
		return {
			'name': self.name,
			'value': self.getValue()
		}

mean_on_flow = lambda axis: OnFlowMetric('mean', (0, 0), lambda curr, new_data: (curr[0] + np.nanmean(new_data, axis=axis), curr[1] + 1), lambda curr: 0 if curr[1] == 0 else (curr[0] / curr[1]))
mean = mean_on_flow(0)

def unziped_batches(iterable, batch_size = 1):
	batch_left = []
	batch_right = []
	for element in iterable:
		batch_left.append(element[0])
		batch_right.append(element[1])
		if len(batch_left) == batch_size:
			yield np.array(batch_left), np.array(batch_right)
			batch_left = []
			batch_right = []
	if len(batch_left) > 0:
		yield np.array(batch_left), np.array(batch_right)

def refreshMetric(metric, batch_and_pairs, examples_limit, log=True):
	if metric.name == 'distribution':
		metric.refresh((*batch_and_pairs, examples_limit), log=log)
		# metric.refresh([batch])
	elif metric.name == 'kmeans':
		metric.refresh(batch_and_pairs)
	else:
		metric.refresh(batch_and_pairs[0])

def getHistogram(image):
	grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	return cv2.calcHist([grayscale], [0], None, [256], [0,256]).reshape(-1)

image_path = 'D:\\datasets\\FMDDS_resized\\medical_mask\\medical_mask\\medical_mask\\images\\0058.jpg'
image = cv2.imread(image_path)
hist = getHistogram(image)
print(hist)
plt.plot(hist)
plt.show()
exit()


hists = getPairsMetricsWithPairs(pairs, 'histogram', threads=16, log=False)
batches = unziped_batches(hists, batch_size = -1)
mean.init()
for data_and_objects_ids in batches:
	hist = data_and_objects_ids[0][0]
	print(hist)
	plt.plot(hist)
	plt.show()
	exit()
	refreshMetric(mean, data_and_objects_ids, 20, log=False)
pairs.setReturnNames(True)
print(mean.getValue())
print(mean.current_value)