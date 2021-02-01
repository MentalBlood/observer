from objects import getObjectPath
from warnings import warn
from files import getFilePath

objects_extensions = ['mp4', 'avi']

classes_names = [['--', '-+'], ['+-', '++']]
def getClasses(pair):
	result = []
	for annotation in pair['annotations']:
		if annotation['arousal'] == None or annotation['valence'] == None:
			continue
		result.append(classes_names[annotation['arousal'] >= 0][annotation['valence'] >= 0])
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
	frame_number = object['number']
	if len(lines) < frame_number + 2:
		return {
			'valence': None,
			'arousal': None
		}
	line_about_object = lines[frame_number + 1]
	if line_about_object == '-5,-5':
		return {
			'valence': None,
			'arousal': None
		}
	numbers_about_object = line_about_object.split(',')
	if numbers_about_object[0] == '' or numbers_about_object[1] == '':
		return {
			'valence': None,
			'arousal': None
		}
	valence = float(numbers_about_object[0])
	arousal = float(numbers_about_object[1])

	return {
		'valence': valence,
		'arousal': arousal
	}

	return {'emotion': label_about_object}

def getAnnotations(object, all_annotations_files):
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
	extracted_annotations = map(lambda c: extractAnnotations(object, c), annotations_files)
	annotations = filter(lambda a: a != None, extracted_annotations)
	return list(annotations)