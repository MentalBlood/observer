import os
import json
from files import getFilePath

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if 'classname' in annotation:
			if annotation['classname'] != None:
				result.append(annotation['classname'])
	return result

def getAnnotationsData(files_metadata):
	joined = {}
	for file_metadata in filter(lambda file_metadata: file_metadata['extension'] == 'json', files_metadata):
		file_path = getFilePath(file_metadata)
		with open(file_path) as file:
			key = file_metadata['name'].split('.')[0]
			joined[key] = json.load(file)
	return joined

def getAnnotations(object, all_annotations_files):
	key = object['name']
	if not (key in all_annotations_files):
		return []
	image_annotation = all_annotations_files[key]
	# if image_annotation['NumOfAnno'] > 1:
	if False:
		return []
	else:
		object_annotations = image_annotation['Annotations']
		return object_annotations