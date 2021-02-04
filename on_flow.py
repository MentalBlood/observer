from tqdm import tqdm
import numpy as np
from classes import class_filter
from functools import partial
import copy
from functools import reduce
import cv2
from objects import readObject
from getImageSize import getImageSize
import json
from json_tools import *
from types import FunctionType
from sklearn.cluster import KMeans

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

def batches(iterable, batch_size = 1):
	batch = []
	for element in iterable:
		batch.append(element)
		if len(batch) == batch_size:
			yield np.array(batch)
			batch = []
	if len(batch) > 0:
		yield np.array(batch)

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

mean_on_flow = lambda axis: OnFlowMetric('mean', (0, 0), lambda curr, new_data: (curr[0] + np.nanmean(new_data, axis=axis), curr[1] + 1), lambda curr: 0 if curr[1] == 0 else (curr[0] / curr[1]))

def kmeans_on_flow(clusters_number):
	def refresh(curr, new_data):
		if curr != None:
			return curr
		n_clusters = min(clusters_number, new_data[1].shape[0])
		labels = KMeans(n_clusters=n_clusters, random_state=0).fit(new_data[0]).labels_
		ids = new_data[1]
		return {str(l): [ids[i] for i in np.where(labels == l)][0] for l in range(n_clusters)}
	return OnFlowMetric('kmeans', None, refresh, lambda curr: curr)

def groups(from_number, to_number, step):
	result = []
	rounding_to = len(str(step).split('.')[1])
	while from_number < to_number:
		temp = round(from_number + step, rounding_to)
		result.append({
			'from': from_number,
			'to': temp,
			'number': 0
		})
		from_number = temp
	return result

def distribution_on_flow(from_number, to_number, step):
	groups_number = (to_number - from_number) / step
	def refresh(curr, new_data, log=True):
		iterator = tqdm(curr, desc='refreshing distribution') if log else curr
		for group in iterator:
			good_values = (new_data > group['from']) * (new_data < group['to'])
			group['number'] += np.sum(good_values)
		return curr
	return OnFlowMetric('distribution', groups(from_number, to_number, step), refresh, lambda curr: curr)

def unnormed_distribution_on_flow(step):
	def refresh(curr, new_data):
		groups_numbers = new_data // step
		unique_groups_numbers, counts = np.unique(groups_numbers, return_counts=True)
		rounding_to = len(str(step).split('.')[1])
		for gn, count in tqdm(zip(unique_groups_numbers, counts), desc='refreshing distribution', total=counts.shape[0]):
			if not (gn in curr):
				curr[int(gn)] = {
					'from': round(gn * step, rounding_to),
					'to': round((gn + 1) * step, rounding_to),
					'number': 0
				}
			curr[gn]['number'] += count
		return curr
	return OnFlowMetric('distribution', {}, refresh, lambda curr: list(curr.values()))

def ndim_unnormed_distribution_on_flow(step):
	def refresh(curr, new_data_and_pairs, log=True):
		new_data = new_data_and_pairs[0]
		if not '.' in str(step):
			rounding_to = 0
		else:
			rounding_to = len(str(step).split('.')[1])
		if len(new_data.shape) > 1:
			tri = new_data * np.tri(*new_data.shape)
			max_value = np.max(new_data)
			trash_symbol = round(max_value + step, rounding_to)
			tri[tri == 0] = trash_symbol
			groups_numbers = np.floor(np.true_divide(tri, step)).astype(int)
			trash_group_number = np.floor(np.true_divide(trash_symbol, step)).astype(int)
			unique_groups_numbers, counts = np.unique(groups_numbers, return_counts=True)
			trash_group_index = np.where(unique_groups_numbers == trash_group_number)[0][0]
			unique_groups_numbers = np.delete(unique_groups_numbers, [trash_group_index])
			counts = np.delete(counts, [trash_group_index])
		else:
			groups_numbers = np.floor(np.true_divide(new_data, step)).astype(int)
			unique_groups_numbers, counts = np.unique(groups_numbers, return_counts=True)
		iterator = zip(unique_groups_numbers, counts)
		iterator = tqdm(iterator, desc='refreshing distribution', total=counts.shape[0]) if log else iterator
		for gn, count in iterator:
			if not (gn in curr):
				curr[gn] = {
					'from': round(gn * step, rounding_to),
					'to': round((gn + 1) * step, rounding_to),
					'number': 0,
					'examples': []
				}
			curr[gn]['number'] += count
		if len(new_data_and_pairs) > 1:
			pairs = new_data_and_pairs[1]
			limit = new_data_and_pairs[2]
			curr_iterator = tqdm(curr, desc='searching for examples') if log else curr
			for group_number in curr_iterator:
				examples_left = limit - len(curr[group_number]['examples'])
				if examples_left != 0:
					indexes = np.vstack(np.where(groups_numbers == group_number)).T
					attempt = 0
					while True:
						attempt += 1
						if indexes.shape[0] > 100 * examples_left:
							required_indexes = indexes[np.random.choice(indexes.shape[0], examples_left, replace=False), :].tolist()
						else:
							np.random.shuffle(indexes)
							required_indexes = indexes[:examples_left].tolist()
						new_examples = [[pairs[i] for i in I] for I in required_indexes]
						break
					curr[group_number]['examples'] += [[pairs[i] for i in I] for I in required_indexes]
		return curr
	return OnFlowMetric('distribution', {}, refresh, lambda curr: list(curr.values()))

def refreshMetric(metric, batch_and_pairs, examples_limit, log=True):
	if metric.name == 'distribution':
		metric.refresh((*batch_and_pairs, examples_limit), log=log)
		# metric.refresh([batch])
	elif metric.name == 'kmeans':
		metric.refresh(batch_and_pairs)
	else:
		metric.refresh(batch_and_pairs[0])

def calculateMetricsOnFlow(values_batches, on_flow_metrics, examples_limit, log=True):
	for metric in on_flow_metrics:
		metric.init()
	for batch_and_pairs in values_batches:
		for metric in on_flow_metrics:
			refreshMetric(metric, batch_and_pairs, examples_limit, log=log)
	result = [metric.getInfo() for metric in on_flow_metrics]
	return result

def calculateOnFlowForClasses(pairs, classes, tasks, report_file_name, get_classes_function, threads, examples_limit=20):
	result = {}
	report = Report(report_file_name)
	pairs.setReturnNames(True)
	for c in classes:
		result[c] = {}
		for task in tasks:
			print('doing task', '"' + task['name'] + '"', 'for class', '"' + c + '":')
			pairs.filterByClass(c)
			pairs.shuffle()
			initial_metric_values = getPairsMetricsWithPairs(pairs, task['initial_metric'], threads=threads, log=(log_level > 1))
			initial_metric_values_batches = task['batcher'](initial_metric_values, batch_size = task['batch_size'])
			preprocessed_batches = map(\
					lambda batch:\
						(reduce(lambda value, f: f(value), task['preprocessing'], batch[0]), batch[1]),\
					initial_metric_values_batches\
				)
			metrics_on_flow = calculateMetricsOnFlow(preprocessed_batches, copy.deepcopy(task['on_flow_metrics']), examples_limit)
			result[c][task['name']] = metrics_on_flow
			report.write(c, result[c])
	pairs.setReturnNames(False)

def loadOnFlowMetric(name, metrics, file_name, filter_as_string):
	if filter_as_string in metrics:
		if name in metrics[filter_as_string]:
			return metrics[filter_as_string][name]
	metrics_from_file = load_json_from_file(file_name)
	if filter_as_string in metrics_from_file:
		if name in metrics_from_file[filter_as_string]:
			return metrics_from_file[filter_as_string][name]
	return None

def calculateOnFlowForFilters(pairs, filters, tasks, report_file_name, threads, examples_limit=20, overwrite=True, log_level=2):
	pairs.dumpFiltersIndexes(filters, overwrite=overwrite)
	report = Report(report_file_name, overwrite=overwrite)
	result = report.get()
	pairs.setReturnNames(True)
	compiled_filters = list(filter(lambda f: len(pairs.filterBy(f)) > 0, compileFilters(filters)))
	if log_level >= 1:
		base_progress_bar_desc = 'Doing tasks'
		progress_bar = tqdm(total = len(compiled_filters) * len(tasks), desc = base_progress_bar_desc)
	for f in compiled_filters:
		pairs.filterBy(f)
		filter_as_string = json.dumps(f)
		if not filter_as_string in result:
			result[filter_as_string] = {}
		for task in tasks:
			if log_level >= 1:
				progress_bar.set_description(base_progress_bar_desc + ' ("' + task['name'] + '" for filter "' + filter_as_string + '")')
			if (task['name'] in result[filter_as_string]) and not ('overwrite' in task):
				progress_bar.set_description(base_progress_bar_desc)
				progress_bar.update(1)
				continue
			pairs.shuffle()
			initial_metric_values = getPairsMetricsWithPairs(iter(pairs), task['initial_metric'], threads=threads, log=(log_level > 1))
			initial_metric_values_batches = task['batcher'](initial_metric_values, batch_size = task['batch_size'])
			if 'values_to_load' in task:
				can_not_load_values_names = []
				fake_globals = globals()
				for v in task['values_to_load']:
					load_result = loadOnFlowMetric(v, result, report_file_name, filter_as_string)
					if load_result == None:
						can_not_load_values_names.append(v)
					else:
						fake_globals[v] = load_result
				if len(can_not_load_values_names) > 0:
					if log_level > 1:
						print('\n\nCan not load values', ', '.join(can_not_load_values_names), 'from filter', filter_as_string, '\n\n')
					progress_bar.update(1)
					continue
				else:
					# print('\n\nloaded metrics', fake_globals, '\n\n')
					task['preprocessing'] = map(lambda f: FunctionType(f.__code__, fake_globals), task['preprocessing'])
			preprocessed_batches = map(\
					lambda batch:\
						(reduce(lambda value, f: f(value), task['preprocessing'], batch[0]), batch[1]),\
					initial_metric_values_batches\
				)
			metrics_on_flow = calculateMetricsOnFlow(preprocessed_batches, copy.deepcopy(task['on_flow_metrics']), examples_limit, log = (log_level > 1))
			result[filter_as_string][task['name']] = metrics_on_flow
			report.write(filter_as_string, result[filter_as_string], dump_now=False)
			if log_level >= 1:
				progress_bar.set_description(base_progress_bar_desc)
			progress_bar.update(1)
		report.dump()
	progress_bar.close()
	pairs.setReturnNames(False)

def getImageSidesRatio(image):
	return image.shape[0] / image.shape[1]

def getImageSidesRatio_fast(image):
	width, height = getImageSize(image)
	return width / height

from pairs import Pairs, compileFilters
from filters import getPairsMetrics, getPairsMetricsWithPairs
from torch_cosine import getCosineDistanceMatrix
from Report import Report
import argparse
from dataset_specific_api import getDatasetSpecificApi

# parsing command line args

parser = argparse.ArgumentParser(description='Calculate on-flow metrics')
parser.add_argument('--dataset', type=str,
                    help='dataset name', default=None)
parser.add_argument('--api', type=str,
                    help='dataset specific api name', default=None)
parser.add_argument('--threads', type=str,
                    help='threads number', default='1')
parser.add_argument('--overwrite', type=str,
                    help='overwrite tasks results or not', default='0')
args = parser.parse_args()

dataset_name = args.dataset
dataset_specific_api_name = args.api or dataset_name
threads = int(args.threads)
overwrite = int(args.overwrite)

# geting dataset specific api
dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)

pairs = Pairs('pairs_' + dataset_name + '_new', get_classes_function=dataset_specific_api.getClasses)
tasks = [{
	'name': 'HOG cosine distances mean and distribution',
	'initial_metric': 'hog',
	'batcher': unziped_batches,
	'batch_size': 30000,
	'preprocessing': [getCosineDistanceMatrix],
	'on_flow_metrics': [mean_on_flow(None), ndim_unnormed_distribution_on_flow(0.1)],
}, {
	'name': 'contrast mean and distribution',
	'initial_metric': 'contrast',
	'batcher': unziped_batches,
	'batch_size': -1,
	'preprocessing': [],
	'on_flow_metrics': [mean_on_flow(None), ndim_unnormed_distribution_on_flow(0.01)]
},{
# 	'name': 'width to height ratios mean and distribution',
# 	'initial_metric': 'self',
# 	'batcher': unziped_batches,
# 	'batch_size': -1,
# 	'preprocessing': [lambda objects: np.array(list(map(lambda o: getImageSidesRatio(readObject(o)), objects)))],
# 	'on_flow_metrics': [mean_on_flow, ndim_unnormed_distribution_on_flow(0.1)]
# }, {
# 	'name': 'width to height ratios mean and distribution (fast version)',
# 	'initial_metric': '__path__',
# 	'batcher': unziped_batches,
# 	'batch_size': -1,
# 	'preprocessing': [lambda paths: np.array(list(map(lambda p: getImageSidesRatio_fast(p), paths)))],
# 	'on_flow_metrics': [mean_on_flow, ndim_unnormed_distribution_on_flow(0.1)]
# }, {
	'name': 'width to height ratios mean and distribution (instant version)',
	'initial_metric': 'width_height_ratio',
	'batcher': unziped_batches,
	'batch_size': -1,
	'preprocessing': [],
	'on_flow_metrics': [mean_on_flow(None), ndim_unnormed_distribution_on_flow(0.1)]
}, {
	'name': 'mean_histogram',
	'initial_metric': 'histogram',
	'batcher': unziped_batches,
	'batch_size': -1,
	'preprocessing': [],
	'on_flow_metrics': [mean_on_flow(0)],
	'overwrite': True
}, {
	'name': 'deviation from mean histogram',
	'initial_metric': 'histogram',
	'batcher': unziped_batches,
	'batch_size': -1,
	'values_to_load': ['mean_histogram'],
	'preprocessing': [lambda batch: np.array(list(map(lambda h: np.linalg.norm(h - mean_histogram[0]['value']), batch)))],
	'on_flow_metrics': [mean_on_flow(None), ndim_unnormed_distribution_on_flow(20)],
	'overwrite': True
}, {
	'name': 'kmeans clastering',
	'initial_metric': 'hog',
	'batcher': unziped_batches,
	'batch_size': -1,
	'preprocessing': [],
	'on_flow_metrics': [kmeans_on_flow(2)]
}]

filters = [{
	'__class__': [[c] for c in pairs.getClasses()]
}]

# calculateOnFlowForClasses(
# 	pairs,
# 	pairs.getClasses(),
# 	tasks,
# 	'on_flow_by_classes_' + dataset_name + '_test.json',
# 	dataset_specific_api.getClasses,
# 	threads=threads
# )

calculateOnFlowForFilters(
	pairs,
	filters,
	tasks,
	'on_flow_by_classes_' + dataset_name + '_test.json',
	threads=threads,
	overwrite=overwrite,
	log_level = 1
)