from pairs import Pairs
from tqdm import tqdm
from random import sample, shuffle
from tqdm import tqdm
from objects import getObjectPath

def countObjectsInClasses(pairs, get_classes_function):
	classes = {}
	for pair in tqdm(pairs, desc='Counting objects in classes'):
		pair_classes = get_classes_function(pair)
		for c in pair_classes:
			if not (c in classes):
				classes[c] = 0
			classes[c] += 1
	return classes

def isFrame(pair):
	return pair['object']['type'] == 'frame'

def countVideosInClasses(pairs, get_classes_function):
	videos_by_classes = {}
	for pair in tqdm(filter(isFrame, pairs), desc='Counting videos in classes'):
		classes = get_classes_function(annotation['emotion'])
		for class_name in classes:
			if not (class_name in videos_by_classes):
				videos_by_classes[class_name] = {}
			video_path = getObjectPath(pair['object'])
			if not (video_path in videos_by_classes[class_name]):
				videos_by_classes[class_name][video_path] = True
	number_of_videos_by_classes = {}
	for class_name in videos_by_classes:
		number_of_videos_by_classes[class_name] = len(videos_by_classes[class_name])
	return number_of_videos_by_classes

def class_filter(class_name, get_classes_function):
	return lambda p: class_name in get_classes_function(p)

def getAllPairsFromClass(pairs, class_name, get_classes_function):
	return filter(class_filter(class_name, get_classes_function), pairs)
	# return tqdm(filter(class_filter(class_name), pairs), desc = 'Geting all pairs from class "' + class_name + '"')

def getRandomPairsFromClass(pairs, class_name, number, get_classes_function):
	all_pairs_from_class = list(getAllPairsFromClass(pairs, class_name, get_classes_function))
	return sample(all_pairs_from_class, number)

def getShuffledPairsFromClass(pairs, class_name):
	pairs.filterByClass(class_name)
	pairs.shuffle()
	return pairs