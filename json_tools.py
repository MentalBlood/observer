import json

def load_json_from_file(file_path):
	result = None
	with open(file_path) as file:
		result = json.load(file)
	return result

def save_as_json(something, file_path):
	with open(file_path, 'w') as file:
		json.dump(something, file)