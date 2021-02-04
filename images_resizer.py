import os
import argparse
from tqdm import tqdm
from shutil import copyfile
from multiprocessing.pool import ThreadPool
from PIL import Image

parser = argparse.ArgumentParser(description='Convert dataset (resize images to fit max width and max height)')
parser.add_argument('--input_dir', type=str,
                    help='input directory', default=None)
parser.add_argument('--output_dir', type=str,
                    help='output directory', default=None)
parser.add_argument('--threads', type=str,
                    help='number of threads', default='1')
parser.add_argument('--max_width', type=str,
					help='max image width', default='2000')
parser.add_argument('--max_height', type=str,
					help='max image height', default='2000')
args = parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
threads = int(args.threads)
max_width = int(args.max_width)
max_height = int(args.max_height)

def resizeImage(image_path, new_image_path):
	image = Image.open(image_path)
	width, height = image.size
	if (width > max_width) or (height > max_height):
		scale = min(max_width / width, max_height / height)
		new_width, new_height = int(width * scale), int(height * scale)
		new_image = image.resize((new_width, new_height))
	else:
		new_image = image
	new_image.save(new_image_path)

def splitToNameAndExtension(file_name):
	last_dot_index = file_name.rfind('.')
	return file_name[:last_dot_index], file_name[last_dot_index+1:]

def resizeAllFromThisDir(input_dir, output_dir, images_extensions, threads):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	images_paths = []
	copy_tasks = []
	print('looking for images...')
	for root, dirs, files in os.walk(input_dir):
		for file in files:
			name, extension = splitToNameAndExtension(file)
			if extension in images_extensions:
				image_path = os.path.normcase(root + '/' + file)
				new_image_path = os.path.normcase(root.replace(input_dir, output_dir) + '/' + file)
				new_image_dir = os.path.dirname(new_image_path)
				if not os.path.exists(new_image_dir):
					os.makedirs(new_image_dir)
				images_paths.append((image_path, new_image_path))
			else:
				new_file_path = os.path.normcase(root.replace(input_dir, output_dir) + '/' + file)
				copy_tasks.append((os.path.normcase(root + '/' + file), new_file_path))
	print('found', len(images_paths), 'images')
	if threads > 1:
		for result in tqdm(ThreadPool(threads).imap_unordered(lambda p: resizeImage(p[0], p[1]), images_paths), desc='Expanding videos from ' + input_dir, total=len(images_paths)):
			pass
	else:
		for result in tqdm(map(lambda p: resizeImage(p[0], p[1]), images_paths), desc='Resizing images from ' + input_dir, total=len(images_paths)):
			pass
	for task in copy_tasks:
		new_dir = os.path.dirname(task[1])
		if not os.path.exists(new_dir):
			os.makedirs(new_dir)
		copyfile(*task)

resizeAllFromThisDir(input_dir, output_dir, ['jpg', 'jpeg', 'png'], threads)