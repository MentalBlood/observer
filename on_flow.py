from tqdm import tqdm
import copy
from functools import reduce
from getImageSize import getImageSize
import json
import numpy as np
from json_tools import *
from types import FunctionType

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
parser.add_argument('--tasks_file', type=str,
                    help='tasks file name (without extension! must be in observer\'s folder)', default='default_tasks')
parser.add_argument('--filters_file', type=str,
                    help='filters file name (without extension! must be in observer\'s folder)', default='default_filters')
args = parser.parse_args()

dataset_name = args.dataset
dataset_specific_api_name = args.api or dataset_name
threads = int(args.threads)
overwrite = int(args.overwrite)
tasks_file_path = args.tasks_file
filters_file_path = args.filters_file

# geting dataset specific api
dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)

pairs = Pairs('pairs_' + dataset_name + '_new', get_classes_function=dataset_specific_api.getClasses)

tasks = __import__(tasks_file_path).tasks
filters = __import__(filters_file_path).filters(pairs.getClasses())

calculateOnFlowForFilters(
	pairs,
	filters,
	tasks,
	'on_flow_metrics_for__' + dataset_name + '.json',
	threads=threads,
	overwrite=overwrite,
	log_level = 1
)