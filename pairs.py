import os
import json
from tqdm import tqdm
from files import getFilePath
from json_tools import *
from Report import *
from random import shuffle
from itertools import product
from functools import reduce
from multiprocessing.pool import ThreadPool

def loadJson(file):
	file_path = getFilePath(file)
	content = None
	with open(file_path) as file:
		content = json.load(file)
	return content

def countJsonFiles(folder_path):
	number = 0
	for element in os.listdir(folder_path):
		if element.split('.')[-1] == 'json':
			number += 1
	return number

def compileFilter(f):
	return [dict(zip(f.keys(), values)) for values in product(*f.values())]

def compileFilters(filters):
	return list(reduce(lambda curr, prev: curr + prev, map(compileFilter, filters), []))

def haveCommonElements(list1, list2):
	return len(list(set(list1).intersection(list2)))

def listsDif(list1, list2):
	return (list(list(set(list1)-set(list2)) + list(set(list2)-set(list1))))

def fitCondition(feature, values, pair, get_classes_function):
	if feature == '__class__':
		return haveCommonElements(get_classes_function(pair), values) == len(values)
	else:
		if not (feature in pair['annotations'][0]):
			return False
		result = False
		featureValueInPair = pair['annotations'][0][feature]
		if featureValueInPair == None:
			return False
		for v in values:
			subresult = True
			if isinstance(v, dict):
				if 'from' in v:
					subresult = subresult and (featureValueInPair >= v['from'])
				if 'to' in v:
					subresult = subresult and (featureValueInPair < v['to'])
			else:
				subresult = subresult and (featureValueInPair == v)
			result = result or subresult
			if result == True:
				return result
		return result

def applyFilter(f, pair, get_classes_function):
	for feature, values in f.items():
		if not fitCondition(feature, values, pair, get_classes_function):
			return False
	return True

class Pairs():
	def __init__(self, folder_path, take_max = -1, get_classes_function = None):
		self.folder_path = folder_path
		self.dataset_name = os.path.basename(folder_path).replace('pairs_', '').replace('_new', '')
		self.take_max = take_max
		self.number_of_files_in_folder = countJsonFiles(folder_path)
		errors_report_path = os.path.normcase(folder_path + '/pairs_errors')
		self.errors_report = Report(errors_report_path)
		self.get_classes_function = get_classes_function
		self.index_file_path = os.path.normcase(self.folder_path + '/classes_index.json')
		self.filters_indexes_file_path = os.path.normcase(self.folder_path + '/filters_indexes.json')
		self.classes_list_file_path = os.path.normcase(self.folder_path + '/classes_list.json')
		self.numbers_from_index = None
		self.took = 0
		self.return_names = False
		if not os.path.exists(self.index_file_path):
			self.dumpClassesIndex()

	def setReturnNames(self, value):
		if value in [True, False]:
			self.return_names = value

	def __iter__(self, from_index=0):
		self.took = from_index
		return self

	def __next__(self):
		if (not self.take_max == -1) and (self.took >= self.take_max):
			raise StopIteration
		name = None
		if self.numbers_from_index == None:
			name = str(self.took)
		else:
			if self.took >= len(self.numbers_from_index):
				raise StopIteration
			name = str(self.numbers_from_index[self.took])
		next_file_metadata = {
			'name': name,
			'extension': 'json',
			'dir': self.folder_path
		}
		next_file_path = getFilePath(next_file_metadata)
		if not os.path.exists(next_file_path):
			raise StopIteration
		content = None
		with open(next_file_path) as next_file:
			try:
				content = json.load(next_file)
			except json.decoder.JSONDecodeError:
				self.errors_report.write(next_file_path, '')
				self.took += 1
				return self.__next__()
		self.took += 1
		if self.return_names:
			return (content, int(name))
		else:
			return content

	def __getitem__(self, i):
		name = None
		if self.numbers_from_index == None:
			name = str(i)
		else:
			if i >= len(self.numbers_from_index):
				raise StopIteration
			name = str(self.numbers_from_index[i])
		return loadJson({
			'name': name,
			'extension': 'json',
			'dir': self.folder_path
		})

	def __len__(self):
		if self.numbers_from_index == None:
			if self.take_max != -1:
				return min(self.take_max, self.number_of_files_in_folder)
			else:
				return self.number_of_files_in_folder
		else:
			if self.take_max != -1:
				return min(self.take_max, self.number_of_files_in_folder, len(self.numbers_from_index))
			else:
				return min(self.number_of_files_in_folder, len(self.numbers_from_index))

	def getClasses(self):
		if not os.path.exists(self.classes_list_file_path):
			self.dumpClasses()
		return load_json_from_file(self.classes_list_file_path)

	def dumpClasses(self, ):
		if not os.path.exists(self.index_file_path):
			self.dumpClassesIndex()
		index = load_json_from_file(self.index_file_path)
		result = []
		for class_name in index:
			result.append(class_name)
		save_as_json(result, self.classes_list_file_path)

	def dumpFiltersIndexes(self, filters, overwrite=True):
		compiled_filters = compileFilters(filters)
		compiled_filters_as_strings = list(map(json.dumps, compiled_filters))
		indexes = None
		ready_compiled_filters_as_strings = []
		if overwrite == False:
			print('checking if filters indexes already exist')
			if os.path.exists(self.filters_indexes_file_path):
				indexes = load_json_from_file(self.filters_indexes_file_path)
				ready_compiled_filters_as_strings = indexes.keys()
				compiled_filters_as_strings = [f for f in compiled_filters_as_strings if not (f in ready_compiled_filters_as_strings)]
				if len(compiled_filters_as_strings) == 0:
					return
				for new_filter in compiled_filters_as_strings:
					indexes[new_filter] = []
		if indexes == None:
			indexes = {s: [] for s in compiled_filters_as_strings}
		self.setReturnNames(True)
		for pair, number in tqdm(self, desc='Creating filters indexes'):
			for i in range(len(compiled_filters_as_strings)):
				f = compiled_filters[i]
				if applyFilter(f, pair, self.get_classes_function):
					key = compiled_filters_as_strings[i]
					indexes[key].append(number)
		save_as_json(indexes, self.filters_indexes_file_path)
		self.setReturnNames(False)

	def filterBy(self, f):
		key = json.dumps(f)
		self.numbers_from_index = load_json_from_file(self.filters_indexes_file_path)[key]
		return self

	def filterByClaster(self, key_filter, claster_id):
		key_filter_as_string = json.dumps(key_filter)
		on_flow_metrics = load_json_from_file('on_flow_by_classes_' + self.dataset_name + '_test.json')
		self.numbers_from_index = on_flow_metrics[key_filter_as_string]['kmeans clastering']['value'][str(claster_id)]
		return self

	def dumpClassesIndex(self):
		index = {}
		for pair in tqdm(self, desc='Creating classes index'):
			classes = self.get_classes_function(pair)
			for c in classes:
				if not (c in index):
					index[c] = []
				index[c].append(self.took - 1)
		save_as_json(index, self.index_file_path)

	def getNumbersFromIndex(self, class_name):
		return load_json_from_file(self.index_file_path)[class_name]

	def filterByClass(self, class_name):
		self.numbers_from_index = self.getNumbersFromIndex(class_name)

	def shuffle(self):
		shuffle(self.numbers_from_index)

	def countObjectsInClasses(self):
		index = load_json_from_file(self.index_file_path)
		result = {}
		for class_name in index:
			result[class_name] = len(index[class_name])
		return result

	def setMax(self, number):
		self.take_max = number

	def setCurrent(self, number):
		self.took = number

	def getNextName(self, number):
		name = None
		if self.numbers_from_index == None:
			name = str(i)
		else:
			if i >= len(self.numbers_from_index):
				raise StopIteration
			name = str(self.numbers_from_index[i])
		return name

	def left(self):
		return len(self) - self.took

	def from_index(self, n):
		return self.__iter__(n)

def check(pairs):
	for pair in tqdm(pairs, desc='Checking pairs for JSON errors'):
		pass