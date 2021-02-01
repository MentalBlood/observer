import os

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	return ['unclassified']

def getAnnotationsData(files_metadata):
	return None

def getAnnotations(object, all_annotations_files):
	object_dir = object['dir']
	object_label = os.path.basename(object_dir)
	return [{}]