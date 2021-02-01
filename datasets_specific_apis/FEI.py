import os
from files import getFilePath
from json_tools import load_json_from_file

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	return [pair['annotations'][0]['emotion']]

def getAnnotationsData(files_metadata):
	return None

def getAnnotations(object, annotations_data):
	object_number_for_person = object['name'].split('-')[1]
	if object_number_for_person == '12':
		return [{'emotion': 'happy'}]
	else:
		return [{'emotion': 'neutral'}]