from tsnecuda import TSNE
import numpy as np
from pairs import Pairs
from filters import getPairsMetrics, getPairsMetricsWithPairs
from dataset_specific_api import getDatasetSpecificApi
import cProfile
from objects import getObjectPath

dataset_name = 'faces_not_clear_2'
clusters_number = 2
dataset_dir = 'pairs_' + dataset_name + '_new'
dataset_specific_api = getDatasetSpecificApi('experiment')
pairs = Pairs(dataset_dir, get_classes_function=dataset_specific_api.getClasses)
# pairs.filterBy({'__class__': ['happy']})

pairs.setReturnNames(True)
hogs_and_pairs = list(getPairsMetricsWithPairs(pairs, 'hog', threads=24))
pairs.setReturnNames(False)
hogs = np.array([e[0] for e in hogs_and_pairs])
print(hogs.shape[0], 'elements')
tsne = TSNE(n_components=2).fit_transform(hogs)
print(tsne)