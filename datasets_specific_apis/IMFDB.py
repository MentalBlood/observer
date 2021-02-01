import os
from files import getFilePath
from json_tools import load_json_from_file
import re

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if annotation['emotion'] != None:
			result.append(annotation['emotion'])
	return result

def getAnnotationsData(files_metadata):
	txt_files = filter(lambda f: f['extension'] == 'txt', files_metadata)
	annotations_data = {}
	for file_data in txt_files:
		file_path = getFilePath(file_data)
		file_content = None
		with open(file_path) as file:
			file_content = file.read()
		if file_content.find('\t') == -1:
			continue
		file_content_lines = filter(lambda l: l != '', file_content.split('\n'))
		for line in file_content_lines:
			splited = re.split('\t| ', line)
			if len(splited) < 12:
				continue
			image_file_name = splited[2]
			emotion = splited[11]
			if emotion == 'FEMALE' or emotion == 'MALE' or emotion == '':
				continue
			dir_name_1 = os.path.basename(os.path.dirname(file_data['dir']))
			dir_name_2 = os.path.basename(file_data['dir'])
			key = '_'.join([dir_name_1, dir_name_2, image_file_name])
			annotations_data[key] = emotion
	return annotations_data

def getAnnotations(object, annotations_data):
	dir_name_1 = os.path.basename(os.path.dirname(os.path.dirname(object['dir'])))
	dir_name_2 = os.path.basename(os.path.dirname(object['dir']))
	image_file_name = object['name'] + '.' + object['extension']
	key = '_'.join([dir_name_1, dir_name_2, image_file_name])
	if not (key in annotations_data):
		return []
	annotation = {'emotion': annotations_data[key]}
	return [annotation]