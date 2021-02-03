from objects import readObject, getObjectPath
from tqdm import tqdm
import copy
import os
import json
import cv2
from multiprocessing.pool import ThreadPool

def filterPairs(pairs, filter_function):
	return filter(lambda i_p: filter_function(i_p[1]), enumerate(pairs))

def getImagesByFilter(pairs, filter_function):
	return map(lambda i_o: (i_o[0], readObject(i_o[1])), map(lambda i_p: (i_p[0], i_p[1]['object']), filterPairs(pairs, filter_function)))

def convert_to_json_serializable(some_object):
	if 'ndarray' in str(type(some_object)):
		return some_object.tolist()
	return some_object

def calculateMetricsForImage(index_and_image, metrics, folder_where_to_write, overwrite):
	index = index_and_image[0]
	new_pair_file_path = os.path.normcase(folder_where_to_write + '/' + str(index) + '.json')
	if os.path.exists(new_pair_file_path):
		with open(new_pair_file_path) as existing_file:
			try:
				new_pair = json.load(existing_file)
			except json.decoder.JSONDecodeError:
				new_pair = index_and_image[1]
	else:
		new_pair = index_and_image[1]
	metrics_data = metrics.items()
	if overwrite == False:
		metrics_data = list(filter(lambda metric_data: not (metric_data[0] in new_pair['annotations'][0]), metrics_data))
	if len(metrics_data) == 0:
		return
	image = readObject(new_pair['object'])
	if type(image) == type(None):
		for metric_name, metric in metrics_data:
			metric_value = None
			new_pair['annotations'][0][metric_name] = metric_value
	else:
		for metric_name, metric in metrics_data:
			try:
				metric_value = metric(image)
			except cv2.error:
				metric_value = None
			serializable_metric_value = convert_to_json_serializable(metric_value)
			new_pair['annotations'][0][metric_name] = serializable_metric_value
		del image
	with open(new_pair_file_path, 'w') as new_pair_file:
		json.dump(new_pair, new_pair_file)
	del new_pair

def getMaxNumberFileName(dir_path):
	result = 0
	for element in os.listdir(dir_path):
		try:
			number = int(element.split('.')[0])
			result = max(result, number)
		except ValueError:
			continue
	return result

def calculateMetricsForImages(pairs, metrics, folder_where_to_write, threads=1, overwrite=False):
	metrics_names = list(metrics.keys())
	from_index = 0
	if not os.path.exists(folder_where_to_write):
		os.mkdir(folder_where_to_write)
	indexes_and_images = enumerate(pairs)
	if threads > 1:
		for result in tqdm(ThreadPool(threads).imap_unordered(\
									lambda i: calculateMetricsForImage(i, metrics, folder_where_to_write, overwrite), indexes_and_images
								), desc = 'Calculating metrics ' + ', '.join(metrics_names), total=len(pairs)):
			pass
	else:
		for i in tqdm(indexes_and_images, total=len(pairs)):
			calculateMetricsForImage(i, metrics, folder_where_to_write, overwrite)

def getObjectMetric(pair, metric_name):
	if metric_name == 'self':
		return pair['object']
	if metric_name == '__path__':
		return getObjectPath(pair['object'])
	annotations = pair['annotations']
	for a in annotations:
		if metric_name in a:
			return a[metric_name]

def getPairsMetrics(pairs, metric_name, threads=1, log=True):
	result = filter(lambda x: x != None, ThreadPool(threads).imap_unordered(lambda p: getObjectMetric(p, metric_name), pairs))
	return tqdm(result, desc = 'Geting metric "' + metric_name + '"', total=len(pairs)) if log else result

def getPairsMetricsWithPairs(pairs, metric_name, threads=1, log=True):
	result = filter(lambda x: (x[0] != None) and (x[0] == x[0]), ThreadPool(threads).imap_unordered(lambda p: (getObjectMetric(p[0], metric_name), p[1]), pairs))
	return tqdm(result, desc = 'Geting metric "' + metric_name + '"') if log else result