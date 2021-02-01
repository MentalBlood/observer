import os
from files import getFilePath
from json_tools import load_json_from_file

objects_extensions = ['jpg', 'jpeg', 'png']

classes_names = [['--', '-+'], ['+-', '++']]
def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		result.append(classes_names[annotation['arousal'] >= 0][annotation['valence'] >= 0])
	return result

def getAnnotationsData(files_metadata):
	json_files = filter(lambda f: f['extension'] == 'json', files_metadata)
	annotations_data = {}
	for file in json_files:
		file_path = getFilePath(file)
		json_from_file = load_json_from_file(file_path)
		key = file['name']
		annotations_data[key] = json_from_file
	return annotations_data

def getAnnotations(object, annotations_data):
	object_dir = object['dir']
	key_for_part = os.path.basename(object_dir)
	annotations_data_part = annotations_data[key_for_part]
	key_for_annotation = object['name']
	annotations = annotations_data_part['frames'][key_for_annotation]
	return [annotations]