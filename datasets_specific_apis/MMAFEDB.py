import os

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if annotation['emotion'] != None:
			result.append(annotation['emotion'])
	return result

def getAnnotationsData(files_metadata):
	return None

def getAnnotations(object, all_annotations_files):
	object_dir = object['dir']
	object_label = os.path.basename(object_dir)
	return [{'emotion': object_label}]