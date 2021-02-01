import os
import csv
from files import getFilePath
from json_tools import load_json_from_file

objects_extensions = ['jpg', 'jpeg', 'png']

classes_names = ['Neutral', 'Happy', 'Sad', 'Surprise', 'Fear', 'Disgust', 'Anger', 'Contempt', 'None', 'Uncertain', 'Non-Face']
def getClasses(pair):
	index = int(pair['annotations'][0]['expression'])
	return [classes_names[index]]


attributes_names = ['face_x', 'face_y', 'face_width', 'face_height', 'facial_landmarks', 'expression', 'valence', 'arousal']
def getAnnotationsData(files_metadata):
	csv_files = filter(lambda f: f['extension'] == 'csv', files_metadata)
	annotations_data = {}
	for file_data in csv_files:
		file_path = getFilePath(file_data)
		with open(file_path) as file:
			reader = csv.reader(file)
			i = 0
			for row in reader:
				if row[0] == 'subDirectory_filePath':
					continue
				image_file_subpath = row[0]
				image_annotation = dict(zip(attributes_names, row[1:]))
				if image_file_subpath in annotations_data:
					print('fuck', image_file_subpath, file_path)
					exit()
				annotations_data[image_file_subpath] = image_annotation

	return annotations_data

def getAnnotations(object, annotations_data):
	object_subpath = os.path.basename(object['dir']) + '/' + object['name'] + '.' + object['extension']
	try:
		annotation = annotations_data[object_subpath]
		return [annotation]
	except KeyError:
		return []