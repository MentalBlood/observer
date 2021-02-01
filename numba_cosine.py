import numpy as np
from numba import vectorize, guvectorize, float32
import math
from timeit import default_timer as timer

@vectorize(['float64(float64, int32)'], target='cuda')
def numba_sqrt(x, count):
    for _ in range(count):
        x = math.sqrt(x)
    return x

@guvectorize([float32(float32[:], float32[:])], '(n),(n)->()', target='cuda')
def distance_cosine(a, b):
    numerator = a.dot(b)
    a2_sum = a.dot(a)
    b2_sum = b.dot(b)
    a_norm = math.sqrt(a2_sum)
    b_norm = math.sqrt(b2_sum)
    denominator = a_norm * b_norm
    result = 1 - numerator / denominator
    return result

# a = np.random.uniform(size = 2048)
# b = np.random.uniform(size = 2048)

# result = numba_sqrt(a, a.shape[0])
# print(result)

result = None
result = distance_cosine(a, b)
print(result)

exit()

@vectorize(['float32(float32, int32)'], target='cpu')
def with_cpu(x, count):
    for _ in range(count):
        x = x - math.sin(x)
    return x
 
@vectorize(['float32(float32, int32)'], target='cuda')
def with_cuda(x, count):
    for _ in range(count):
        x = x - math.sin(x)
    return x
 
data = np.random.uniform(-3, 3, size=1000000).astype(np.float32)
 
for c in [1, 10, 100]:
    print(c)
    for f in [with_cpu, with_cuda]:
        start = timer()
        r = f(data, c)
        end = timer()
        elapsed_time = end - start
        print('time:', elapsed_time)