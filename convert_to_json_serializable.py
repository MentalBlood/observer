import numpy as np

def convert_to_json_serializable(o):
	if isinstance(o, np.ndarray):
		return o.tolist()
	if isinstance(o, np.int32) or isinstance(o, np.int64):
		return int(o)