import os

objects_extensions = ['jpg', 'jpeg', 'png']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if annotation['mask'] != None:
			result.append(annotation['mask'])
	return result

def getAnnotationsData(files_metadata):
	return None

def getAnnotations(object, all_annotations_files):
	object_dir = object['dir']
	object_label = 'mask' if 'masked' in os.path.basename(os.path.dirname(object_dir)) else 'no mask'
	return [{'mask': object_label}]