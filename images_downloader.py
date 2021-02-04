import csv
import os
from json_tools import save_as_json, load_json_from_file
import requests
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
import argparse

parser = argparse.ArgumentParser(description='Download images from links listed in JSON')
parser.add_argument('--input', type=str,
                    help='json with links file path', default=None)
parser.add_argument('--output', type=str,
                    help='dir where to save images', default=None)
parser.add_argument('--threads', type=str,
                    help='threads number', default=1)
parser.add_argument('--overwrite', type=str,
                    help='overwrite images or not', default=0)
args = parser.parse_args()

input_path = args.input
output_path = args.output
threads = int(args.threads)
overwrite = int(args.overwrite)

extensions = ['.jpg', '.jpeg', '.png']
def downloadImage(link_and_label, dir_path, image_file_name):
	link = link_and_label[0]
	label = link_and_label[1]
	image_path = os.path.normcase(dir_path + '/' + image_file_name + '__label__' + label + '.jpg')
	# if os.path.exists(image_path) or os.path.exists(failed_image_path):
	# 	return
	try:
		response = requests.get(link, stream=True)
	except (requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects, requests.exceptions.ReadTimeout) as e:
		failed_image_path = image_path + '.failed'
		with open(failed_image_path, 'w') as failed_image:
			pass
		return
	if not response.ok:
		failed_image_path = image_path + '.failed'
		with open(failed_image_path, 'w') as failed_image:
			pass
		return
	with open(image_path, 'wb') as file:
		file.write(response.content)
		# for block in response.iter_content(8192):
		# 	if not block:
		# 		break
		# 	handle.write(block)

def getMaxNumberFileName(dir_path):
	result = 0
	for element in os.listdir(dir_path):
		number = int(element.split('.')[0])
		result = max(result, number)
	return result

def downloadImages(links, dir_path):
	from_index = 0
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)
	elif (not overwrite):
		last_saved_image_number = getMaxNumberFileName(dir_path)
		from_index = max(0, last_saved_image_number - threads)
		links = links[from_index:]
	for result in tqdm(ThreadPool(threads).imap_unordered(lambda n_link: downloadImage(n_link[1], dir_path, str(n_link[0] + from_index)), enumerate(links)), total = len(links)):
		pass

links = list(load_json_from_file(input_path).items())
downloadImages(links, output_path)