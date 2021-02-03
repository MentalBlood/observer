import json
import matplotlib.pyplot as plt
from math import log, ceil
import numpy as np
from json_tools import load_json_from_file
from show import showFromClass, showPairsImages
from pairs import Pairs
from dataset_specific_api import getDatasetSpecificApi
from multiprocessing.pool import ThreadPool
from presentFilter import presentFilter
from objects import getObjectPath
from math import sqrt

def showBarPlot(x, y, vertical=True):
	if vertical:
		max_x_label_length = max(map(lambda number: len(str(number).replace('.', '')), x))
		height = max(len(y) / 4, 4)
		width = max(len(x) / 2 / 4 * max_x_label_length, 6)
		fig = plt.figure(figsize=(width, height))
	else:
		max_y_label_length = max(map(lambda number: len(str(number).replace('.', '')), y))
		height = max(len(x) / 4, 4)
		width = max(len(y) / 2 / 4 * sqrt(max_y_label_length), 6)
		fig = plt.figure(figsize=(width, height))
	ax = fig.add_axes([0,0,1,1])
	if vertical:
		ax.bar(x, y)
	else:
		ax.barh(x, y)
	plt.show()

def plotClassesDistribution(classes, vertical=True):
	x = list(classes.keys())
	y = list(classes.values())
	showBarPlot(x, y, vertical)

def plotDatasetClassesDistribution(dataset_name, vertical=True):
	report_file_name = 'report_' + dataset_name + '.json'
	report = load_json_from_file(report_file_name)
	plotClassesDistribution(report['objects number by class'], vertical)

def datasetClasses(dataset_name, vertical=True, total=None):
	report_file_name = 'report_' + dataset_name + '.json'
	report = load_json_from_file(report_file_name)
	print(len(report['objects number by class']), 'классов:')
	for c in report['objects number by class']:
		print('{0:20}'.format('Класс "' + c + '":'), report['objects number by class'][c], 'изображений')
	print()
	print('{0:20}'.format('Всего:'), total if total else len(Pairs('pairs_' + dataset_name)), 'изображений')
	print()
	plotClassesDistribution(report['objects number by class'], vertical)

def datasetClassExampleImages(dataset_name, class_name, number_of_images = 12, api = None):
	pairs_folder_name = 'pairs_' + dataset_name
	dataset_specific_api_name = api or dataset_name
	dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)
	pairs = Pairs(pairs_folder_name, get_classes_function=dataset_specific_api.getClasses)
	showFromClass(pairs, class_name, number_of_images, 1, number_of_images)

def datasetClassesExampleImages(dataset_name, number_of_images = 12, api = None):
	pairs_folder_name = 'pairs_' + dataset_name
	dataset_specific_api_name = api or dataset_name
	dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)
	pairs = Pairs(pairs_folder_name, get_classes_function=dataset_specific_api.getClasses)
	classes = pairs.getClasses()
	for class_name in classes:
		print('Примеры изображений из класса "' + class_name + '":')
		showFromClass(pairs, class_name, number_of_images, rows=1, columns=number_of_images)

def scalePlotDensity(x, y, scaleFactor):
	return x[::scaleFactor], y[::scaleFactor]

def plotDistribution(distribution, preprocess, trim_zeros = True, vertical = True, scaleFactor=2):
	x = []
	y = []
	for segment in distribution:
		x.append(str(round((segment['from'] + segment['to']) / 2, 2)))
		y.append(preprocess(segment['number']))
	if trim_zeros:
		while len(y) and (y[-1] == 0):
			x.pop()
			y.pop()
	x, y = scalePlotDensity(x, y, scaleFactor)
	showBarPlot(x, y, vertical)

# def datasetMetrics_old(dataset_name, metric_name, log_plots = False, api = None):
# 	report_file_name = 'on_flow_by_classes_' + dataset_name + '.json'
# 	report = load_json_from_file(report_file_name)
# 	pairs_folder_name = 'pairs_' + dataset_name
# 	dataset_specific_api_name = api or dataset_name
# 	dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)
# 	pairs = Pairs(pairs_folder_name, get_classes_function=dataset_specific_api.getClasses)
# 	for class_name in report:
# 		print('Для класса "' + class_name + '":')
# 		report_for_class = report[class_name]
# 		metrics_for_class = report_for_class[metric_name]
# 		for metric in metrics_for_class:
# 			if metric['name'] == 'distribution':
# 				print('Распределение:')
# 				preprocess = (lambda x: log(x) if x != 0 else 0) if log_plots else (lambda x: x)
# 				plotDistribution(metric['value'], preprocess)
# 				for interval in metric['value']:
# 					if 'examples' in interval:
# 						print('Примеры для интервала с', interval['from'], 'до', interval['to'], ':')
# 						if len(interval['examples'][0]) == 1:
# 							example_pairs = [pairs[example[0]] for example in interval['examples']]
# 							showPairsImages(example_pairs)
# 						else:
# 							for example in interval['examples']:
# 								example_pairs = [pairs[i] for i in example]
# 								showPairsImages(example_pairs)
# 			elif metric['name'] == 'mean':
# 				print('Среднее значение:', metric['value'])

def printPairsPaths(pairs):
	for p in pairs:
		print(getObjectPath(p['object']))

proper_endings = {
	'0': 'ов',
	'1': '',
	'2': 'а',
	'3': 'а',
	'4': 'а',
	'5': 'ов',
	'6': 'ов',
	'7': 'ов',
	'8': 'ов',
	'9': 'ов'
}
def properEnding(number):
	return proper_endings[str(number)[-1]]

def datasetMetrics(dataset_name, metric_name, log_plots = False, api = None, examples_amount=0, rows=None, columns=None, vertical=True, max_columns=20):
	examples_amount = None if (examples_amount == 'all') else examples_amount
	report_file_name = 'on_flow_by_classes_' + dataset_name + '_test.json'
	report = load_json_from_file(report_file_name)
	pairs_folder_name = 'pairs_' + dataset_name
	dataset_specific_api_name = api or dataset_name
	dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)
	if (examples_amount == None) or (examples_amount > 0):
		pairs = Pairs(pairs_folder_name, get_classes_function=dataset_specific_api.getClasses)
	for filter_as_string in report:
		print('Для изображений', presentFilter(json.loads(filter_as_string)) + ':')
		report_for_filter = report[filter_as_string]
		metrics_for_class = report_for_filter[metric_name]
		for metric in metrics_for_class:
			if metric['name'] == 'distribution':
				print('Распределение:')
				preprocess = (lambda x: log(x) if x != 0 else 0) if log_plots else (lambda x: x)
				if len(metric['value']) > max_columns:
					scaleFactor = ceil(len(metric['value']) / max_columns)
				else:
					scaleFactor = 1
				plotDistribution(metric['value'], preprocess, vertical=vertical, scaleFactor=scaleFactor)
				for interval in metric['value']:
					if (examples_amount == None) or (examples_amount > 0):
						if 'examples' in interval:
							print('Примеры для интервала с', interval['from'], 'до', interval['to'], ':')
							if len(interval['examples'][0]) == 1:
								example_pairs = [pairs[example[0]] for example in interval['examples'][:examples_amount]]
								showPairsImages(example_pairs)
							else:
								for example in interval['examples'][:examples_amount]:
									example_pairs = [pairs[i] for i in example]
									showPairsImages(example_pairs)
			elif (metric['name'] == 'kmeans') and ((examples_amount == None) or (examples_amount > 0)):
				print('Результаты кластеризации на', len(metric['value']), 'кластер' + properEnding(len(metric['value'])) + ':')
				for cluster_id in metric['value']:
					print('Примеры изображений из кластера ' + cluster_id + ':')
					example_pairs = [pairs[object_id] for object_id in metric['value'][cluster_id][:examples_amount]]
					if len(example_pairs) > 0:
						showPairsImages(example_pairs)
			elif metric['name'] == 'mean':
				if metric_name == 'mean_histogram':
					plt.plot(metric['value'], color='black')
					plt.show()
				else:
					print('Среднее значение:', metric['value'])