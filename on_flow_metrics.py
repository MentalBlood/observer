import numpy as np
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

mean_on_flow = lambda axis: OnFlowMetric('mean', (0, 0), lambda curr, new_data: (curr[0] + np.nanmean(new_data, axis=axis), curr[1] + 1), lambda curr: 0 if curr[1] == 0 else (curr[0] / curr[1]))