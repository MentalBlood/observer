import os
import cv2
from pairs import Pairs
from hog import getHog
from contrast import getImageContrast
from classes import class_filter
from filters import calculateMetricsForImages
from show import showContinuously, showFromClassContinuously
from Report import Report
import argparse
from dataset_specific_api import getDatasetSpecificApi

# parsing command line args

parser = argparse.ArgumentParser(description='Calculate objects metrics')
parser.add_argument('--dataset', type=str,
                    help='dataset name', default=None)
parser.add_argument('--api', type=str,
                    help='dataset specific api name', default=None)
parser.add_argument('--threads', type=str,
                    help='threads number', default='1')
parser.add_argument('--overwrite', type=str,
                    help='overwrite existing pairs or not', default='0')
parser.add_argument('--continue_calc', type=str,
                    help='continue first calculatinon', default='1')
parser.add_argument('--metrics_file', type=str,
                    help='metrics file name (without extension! must be in observer\'s folder)', default='default_metrics')
args = parser.parse_args()

dataset_name = args.dataset
dataset_specific_api_name = args.api or dataset_name
threads = int(args.threads)
overwrite = int(args.overwrite)
continue_calc = int(args.continue_calc)
metrics_file_path = args.metrics_file

# importing metrics
metrics = __import__(metrics_file_path).metrics

# creating report object
report_file_path = 'report_' + dataset_name + '.json'
if overwrite or (not os.path.exists(report_file_path)):
	report = Report(report_file_path)

# geting dataset specific api
dataset_specific_api = getDatasetSpecificApi(dataset_specific_api_name)

# geting pairs from directory
directory = 'pairs_' + dataset_name + '_new'
if overwrite or (not os.path.exists(directory)) or continue_calc:
	directory = directory.replace('_new', '')
pairs = Pairs(directory, get_classes_function=dataset_specific_api.getClasses)



# using this function you can see and list (press q) images with from class
# showFromClassContinuously(pairs, 'Unknown', dataset_specific_api.getClasses)



# counting objects in classes
if overwrite or (not os.path.exists(report_file_path)):
	objects_number_by_class = pairs.countObjectsInClasses()
	report.write('objects number by class', objects_number_by_class)



# counting videos in classes
# videos_number_by_class = countVideosInClasses(pairs, dataset_specific_api.getClasses)
# report.write('videos number by class', videos_number_by_class)

# available metrics


# calculating metrics
new_pairs_folder_path = 'pairs_' + dataset_name + '_new'
calculateMetricsForImages(pairs, metrics, new_pairs_folder_path, threads=threads, overwrite=overwrite)
# if overwrite:
# 	pairs.dumpClasses(os.path.normcase(new_pairs_folder_path + '/' + 'classes_list.json'))