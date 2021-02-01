import os
from files import getFilePath
from objects import getObjectPath

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		result += list(filter(lambda key: annotation['attr'][key] == '1', annotation['attr'].keys()))
	return result

def getAnnotationsData(files_metadata):
	result = {}
	for file_metadata in files_metadata:
		if file_metadata['extension'] == 'txt':
			attributes_group_name = '_'.join(file_metadata['name'].split('_')[1:-1])
			with open(getFilePath(file_metadata)) as f:
				f.readline()
				attributes_names = f.readline()[:-1].split(' ')
				if attributes_group_name == 'bbox':
					attributes_names = attributes_names[1:]
				for line in f:
					line_without_multiple_spaces = ' '.join(line.split())
					line_splited = line_without_multiple_spaces[:-1].split(' ')
					image_file_name = line_splited[0]
					attributes_values = line_splited[1:]
					if not (image_file_name in result):
						result[image_file_name] = {}
					result[image_file_name][attributes_group_name] = dict(zip(attributes_names, attributes_values))
	return result

def getAnnotations(object, annotations_data):
	key = object['name'] + '.jpg'
	if key in annotations_data:
		return [annotations_data[key]]
	else:
		return []