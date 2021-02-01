import mxnet as mx
import time
import cProfile

def batch_cosine_dist(a, b):
	a1 = mx.nd.expand_dims(a, axis=1)
	b1 = mx.nd.expand_dims(b, axis=2)
	d = mx.nd.batch_dot(a1, b1)[:,0,0]
	a_norm = mx.nd.sqrt(mx.nd.sum((a*a), axis=1))
	b_norm = mx.nd.sqrt(mx.nd.sum((b*b), axis=1))
	dist = 1.0 - d / (a_norm * b_norm)
	mx.nd.waitall()
	return dist

def experiment():
	print('started')
	batch_size = 100000
	dim = 256
	ctx = mx.npx.gpu()
	a = mx.random.uniform(shape=(batch_size, dim), ctx=ctx)
	b = mx.random.uniform(shape=(batch_size, dim), ctx=ctx)
	print('initialized', a.shape)
	dist = batch_cosine_dist(a, b)
	return dist

def concat(a, b):
	a_expanded = a.expand_dims(0)
	b_expanded = b.expand_dims(0)
	result = mx.nd.concat(a, b, dim=0)
	return result

def repeat(v, count):
	v_expanded = v.expand_dims(0)
	result = v_expanded
	for i in range(count - 1):
		result = mx.nd.concat(result, v_expanded, dim=0)
	return result

def experiment1():
	print('started')
	batch_size = 100
	dim = 256
	ctx = mx.npx.gpu()
	vectors = mx.random.uniform(shape=(batch_size, dim), ctx=ctx)
	print('initialized', vectors.shape)
	matrix = mx.ndarray.empty([batch_size, batch_size], ctx=ctx)
	for i in range(batch_size):
		a = repeat(vectors[i], batch_size)
		matrix[i] = batch_cosine_dist(a, vectors)
	print(matrix.shape)
	return matrix

class PairsIterator():
	def __init__(self, n):
		self.n = n

	def __iter__(self):
		self.current_pair_index = 0
		self.last_pair_index = self.n ** 2 - 1
		return self

	def __next__(self):
		if self.current_pair_index > self.last_pair_index:
			raise StopIteration
		result = (self.current_pair_index // self.n, self.current_pair_index % self.n)
		self.current_pair_index += 1
		return result

	def pairs_left(self):
		return self.last_pair_index + 1 - self.current_pair_index

def set(a, i, b):
	a[i] = b

def prepare_pairs(a, b, pairs_iterator, requested_number, vectors, ctx):
	number = min(requested_number, pairs_iterator.pairs_left())
	if number == 0:
		raise StopIteration
	for i in range(number):
		new_pair = next(pairs_iterator)
		set(a, i, vectors[new_pair[0]])
		set(b, i, vectors[new_pair[1]])
		# a[i] = vectors[new_pair[0]]
		# b[i] = vectors[new_pair[1]]
	return a, b

def experiment2(number_of_vectors, dim, batch_size):
	print('started')
	ctx = mx.npx.gpu()
	vectors = mx.random.uniform(shape=(number_of_vectors, dim), ctx=ctx)
	pairs_iterator = iter(PairsIterator(number_of_vectors))
	a = mx.nd.empty(shape=(batch_size, vectors.shape[1]), ctx=ctx)
	b = mx.nd.empty(shape=(batch_size, vectors.shape[1]), ctx=ctx)
	print('initialized', vectors.shape)

	# matrix = mx.ndarray.empty([number_of_vectors, number_of_vectors], ctx=ctx)
	while True:
		try:
			prepare_pairs(a, b, pairs_iterator, batch_size, vectors, ctx)
		except StopIteration:
			break
		batch_cosine_dist(a, b)

# a = mx.nd.array([1, 2, 3])
# a = repeat(a, 3)
# b = mx.nd.array([4, 5, 6])
# b = repeat(b, 2)
# result = concat(a, b)
# print(result)

# vectors = mx.random.uniform(shape=(3, 5))
# pairs = iter(PairsIterator(3))
# print(prepare_pairs(pairs, 100, vectors))

cProfile.run('experiment2(200, 256, 40000)')

# def f(a):
# 	a[0] = 42

# ctx = mx.npx.gpu()
# m = mx.nd.array([1, 2, 3], ctx=ctx)
# print(m)
# f(m)
# print(m)


# 1. Проверить правильно ли OpenCV считает кадры
# 2. Начать применять инструменты к датасетам