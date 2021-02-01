from objects import getObjectPath
from warnings import warn
from files import getFilePath

objects_extensions = ['mp4', 'avi']

def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if annotation['emotion'] != None:
			result.append(annotation['emotion'])
	return result

def getAnnotationsDataForExtensions(files_metadata, extensions):
	joined = {}
	for file_metadata in filter(lambda file_metadata: file_metadata['extension'] in extensions, files_metadata):
		file_path = getFilePath(file_metadata)
		with open(file_path) as file:
			key = file_path
			content = file.read().split('\n')
			joined[key]= content
	return joined

def getAnnotationsData(files_metadata):
	return getAnnotationsDataForExtensions(files_metadata, ['txt'])

def getAnnotationsFilesPrefix(object_file_path):
	result = object_file_path.replace('\\videos\\', '\\annotations\\').replace('/videos/', '/annotations/')
	ext_dot_index = result.rfind('.')
	result = result[:ext_dot_index]
	return result

def extractAnnotations(object, annotations_file):
	lines = annotations_file['content']
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

def getAnnotations(object, all_annotations_files):
	object_file_path = getObjectPath(object)
	# if object['name'] == '122-60-1920x1080-5':
	# 	print(object_file_path)
	annotations_files_paths_prefix = getAnnotationsFilesPrefix(object_file_path)
	# if object['name'] == '122-60-1920x1080-5':
	# 	print(annotations_files_paths_prefix)
	possible_annotations_files_paths = [
		annotations_files_paths_prefix + '.txt',
		annotations_files_paths_prefix + '_left.txt',
		annotations_files_paths_prefix + '_right.txt'
	]
	# if object['name'] == '122-60-1920x1080-5':
	# 	print(possible_annotations_files_paths)
	annotations_files = [{
		'path': path,
		'content': all_annotations_files[path]
	} for path in filter(lambda p: p in all_annotations_files, possible_annotations_files_paths)]
	extracted_annotations = map(lambda c: extractAnnotations(object, c), annotations_files)
	annotations = filter(lambda a: a != None, extracted_annotations)
	return list(annotations)