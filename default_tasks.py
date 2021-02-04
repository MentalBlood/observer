import numpy as np
from on_flow_metrics import *
from torch_cosine import getCosineDistanceMatrix

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