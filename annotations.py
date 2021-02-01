import os
import json
from files import getFilePath
from objects import getObjectPath
from warnings import warn

def joinAnnotations(files_metadata, extensions):
	joined = {}
	for file_metadata in filter(lambda file_metadata: file_metadata['extension'] in extensions, files_metadata):
		file_path = getFilePath(file_metadata)
		with open(file_path) as file:
			key = file_path
			content = file.read()
			joined[key]= content
	return joined

def getAnnotationsFilesPrefix(object_file_path):
	result = object_file_path.replace('\\videos\\', '\\annotations\\')
	ext_dot_index = result.rfind('.')
	result = result[:ext_dot_index]
	return result

def exprExtractAnnotations(object, annotations_file):
	lines = annotations_file['content'].split('\n')
	labels = lines[0].split(',')
	frame_number = object['number']
	line_about_object = lines[frame_number + 1]
	label_about_object = None
	if line_about_object == '-1':
		label_about_object = 'Unknown'
	else:
		try:
			label_about_object = labels[int(line_about_object)]
		except ValueError:
			warning_info = 'found no annotation for object ' + str(object) + ' in file ' + annotations_file['path']
			warn(warning_info, UserWarning)
			return None

	return {'emotion': label_about_object}

def exprGetAnnotations(object, all_annotations_files, extractAnnotationsFunction = exprExtractAnnotations):
	object_file_path = getObjectPath(object)
	annotations_files_paths_prefix = getAnnotationsFilesPrefix(object_file_path)
	possible_annotations_files_paths = [
		annotations_files_paths_prefix + '.txt',
		annotations_files_paths_prefix + '_left.txt',
		annotations_files_paths_prefix + '_right.txt'
	]
	annotations_files = [{
		'path': path,
		'content': all_annotations_files[path]
	} for path in filter(lambda p: p in all_annotations_files, possible_annotations_files_paths)]
	extracted_annotations = map(lambda c: exprExtractAnnotations(object, c), annotations_files)
	annotations = filter(lambda a: a != None, extracted_annotations)
	return list(annotations)