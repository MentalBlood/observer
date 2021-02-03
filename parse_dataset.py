import json
import os
import argparse
from tqdm import tqdm
from files import getFiles
from objects import *
from dataset_specific_api import getDatasetSpecificApi



# parsing command line args

parser = argparse.ArgumentParser(description='Parse dataset and save pairs object-annotations')
parser.add_argument('--input', type=str,
                    help='path to dataset directory', default=None)
parser.add_argument('--dataset_name', type=str,
                    help='dataset name', default=None)
parser.add_argument('--output_pairs', type=str,
                    help='directory where to save pairs object-annotations', default=None)
parser.add_argument('--api', type=str,
					help='dataset specific api name', default=None)
parser.add_argument('--overwrite', type=str,
					help='overwrite existing pairs or not', default='1')
parser.add_argument('--splited', type=str,
					help='is dataset splited by frames', default='0')
args = parser.parse_args()

dataset_folder = args.input
dataset_name = args.dataset_name or os.path.basename(dataset_folder)
pairs_folder_path = args.output_pairs or 'pairs_' + dataset_name
dataset_specific_api_name = args.api or dataset_name
overwrite = int(args.overwrite)
splited = int(args.splited)



# geting files

print('geting files...')
files = getFiles(dataset_folder)
print('got', len(files), 'files')



# geting dataset specific api

dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name, splited_by_frames=splited)



# creating objects iterator

print('creating objects iterator...')
objects = iter(Objects(files, dataset_specific_api.objects_extensions))
print('created')



# geting annotations data

print('geting annotations data...')
annotations_data = dataset_specific_api.getAnnotationsData(files)
print('got')



# creating pairs object-annotations

if not os.path.exists(pairs_folder_path):
	os.mkdir(pairs_folder_path)
current_object_index = 0
classes = {}
for object in tqdm(objects, desc='Creating pairs object-annotations'):
	new_pair_file_path = os.path.normcase(pairs_folder_path + '/' + str(current_object_index) + '.json')
	if (not overwrite) and os.path.exists(new_pair_file_path):
		continue
	annotations = dataset_specific_api.getAnnotations(object, annotations_data)
	if len(annotations) > 0:
		new_pair = {
			'object': object,
			'annotations': annotations
		}
		with open(new_pair_file_path, 'w') as new_pair_file:
			json.dump(new_pair, new_pair_file)
		new_pair_classes = dataset_specific_api.getClasses(new_pair)
		for c in new_pair_classes:
			classes[c] = True
		current_object_index += 1
classes_list = list(classes.keys())
print('created', current_object_index, 'pairs from', len(classes_list), 'classes:', classes_list)
classes_list_file_path = os.path.normcase(pairs_folder_path + '/' + 'classes_list.json')
with open(classes_list_file_path, 'w') as classes_list_file:
	json.dump(classes_list, classes_list_file)