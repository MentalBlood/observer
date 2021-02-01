import os

def getAnnotationsSplitedDecorator(getAnnotations):
	def decoratedFunction(object, all_annotations_files):
		print('decoratedFunction')
		identificator = '__frame__'
		if object['name'].startswith(identificator):
			fake_object = {
				'type': 'frame',
				'number': int(object['name'].replace(identificator, '')),
				'name': os.path.basename(object['dir']),
				'extension': None,
				'dir': os.path.dirname(object['dir'])
			}
			return getAnnotations(fake_object, all_annotations_files)
		else:
			return getAnnotations(object, all_annotations_files)
	return decoratedFunction

def getDatasetSpecificApi(dataset_name, splited_by_frames=False):
	import_result = __import__('datasets_specific_apis.' + dataset_name)
	api = getattr(import_result, dataset_name)
	# print(dir(api))
	if splited_by_frames:
		api.getAnnotations = getAnnotationsSplitedDecorator(api.getAnnotations)
		api.objects_extensions = ['png', 'jpeg', 'jpg']
	return api

# getDatasetSpecificApi('aff_wild2_expr')