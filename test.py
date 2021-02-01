from sklearn.cluster import KMeans
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
kmeans = KMeans(n_clusters=clusters_number, random_state=0).fit(hogs)

labels = kmeans.labels_
ids = np.array([e[1] for e in hogs_and_pairs])

result = {l: [ids[i] for i in np.where(labels == l)][0] for l in range(clusters_number)}

for cluster_id in result:
	print(cluster_id)
	for object_id in result[cluster_id]:
		object = pairs[object_id]['object']
		print(getObjectPath(object))

# import torch
# from kmeans_pytorch import kmeans

# # kmeans
# cProfile.run("cluster_ids_x, cluster_centers = kmeans(X=torch.from_numpy(hogs), num_clusters=clusters_number, distance='cosine', device=torch.device('cuda'))")