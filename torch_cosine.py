import torch
import pytorch_lightning
import numpy as np
import cProfile

calc = pytorch_lightning.metrics.functional.self_supervised.embedding_similarity

def experiment(mode):
	number = 60000
	dim = 2304
	tensor = torch.rand(number, dim, device=torch.device(mode))
	result = calc(tensor, similarity='cosine')
	print(result.shape)
	return result.cpu().numpy()

# cProfile.run("experiment('cpu')")
# cProfile.run("experiment('cuda')")

def getCosineDistanceMatrix(vectors):
	vectors = vectors[~np.all(vectors == 0, axis=1)]
	tensor = torch.tensor(vectors, device = torch.device('cpu'))
	result = calc(tensor, similarity='cosine').cpu().numpy()
	result[result > 1.] = 0.999999
	return result

# def getUndoubledValuesFromMatrix_slow(matrix):
# 	result = np.array([])
# 	for i in range(matrix.shape[0]):
# 		result = np.concatenate((result, matrix[i][i + 1 :]))
# 	return result

def getUndoubledValuesFromMatrix(matrix):
	matrix *= np.tri(*matrix.shape)
	return matrix[np.nonzero(matrix)]

# number = 10000
# dim = 2304
# tensor = torch.rand(number, dim, device=torch.device('cpu'))
# matrix = calc(tensor, similarity='cosine').cpu().numpy()
# a = None
# b = None
# cProfile.run('b = getUndoubledValuesFromMatrix(matrix)')
# cProfile.run('a = getUndoubledValuesFromMatrix_slow(matrix)')
# print(a.shape, b.shape)

class CosineDistances():
	def __init__(self, vectors, batch_size, return_type='matrix'):
		self.vectors = iter(vectors)
		self.batch_size = batch_size
		self.return_type = return_type

	def __iter__(self):
		return self

	def __next__(self):
		batch = []
		for vector in self.vectors:
			batch.append(vector)
			if len(batch) == self.batch_size:
				break
		if len(batch) == 0:
			raise StopIteration
		matrix = getCosineDistanceMatrix(batch)
		if self.return_type == 'matrix':
			return matrix
		elif self.return_type == 'undoubled_values':
			return getUndoubledValuesFromMatrix(matrix)

# from pairs import Pairs
# from filters import getPairsMetrics
# from on_flow import calculateMetricsOnFlow, mean_on_flow

# def test():
# 	pairs = Pairs('pairs_hog')
# 	pairs_from_class = getAllPairsFromClass(pairs, 'Happiness')
# 	hogs = getPairsMetrics(pairs_from_class, 'hog')
# 	cosine_distances = CosineDistances(hogs, 1000, return_type='undoubled_values')
# 	calculateMetricsOnFlow(cosine_distances, [mean_on_flow])