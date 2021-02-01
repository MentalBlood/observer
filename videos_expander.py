import cv2
import os
import argparse
from tqdm import tqdm
from shutil import copyfile
from multiprocessing.pool import ThreadPool

parser = argparse.ArgumentParser(description='Parse dataset and save pairs object-annotations')
parser.add_argument('--input_dir', type=str,
                    help='csv file path', default=None)
parser.add_argument('--output_dir', type=str,
                    help='links json file path', default=None)
parser.add_argument('--threads', type=str,
                    help='number of threads', default='1')
parser.add_argument('--identifier', type=str,
					help='prefix for frames files names', default='__frame__')
args = parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
threads = int(args.threads)
identifier = args.identifier

def expandVideo(video_path, frames_dir, extension):
	if not os.path.exists(frames_dir):
		os.makedirs(frames_dir)
	video = cv2.VideoCapture(video_path)
	frame_number = 0
	with tqdm(total=int(video.get(cv2.CAP_PROP_FRAME_COUNT)), desc='Expanding ' + video_path + ' to ' + frames_dir + ' as ' + extension) as progress_bar:
		while True:
			frame = video.read()
			if not frame[0]:
				break
			frame_path = os.path.normcase(frames_dir + '/' + identifier + str(frame_number) + '.' + extension)
			cv2.imwrite(frame_path, frame[1])
			frame_number += 1
			progress_bar.update(1)

def splitToNameAndExtension(file_name):
	last_dot_index = file_name.rfind('.')
	return file_name[:last_dot_index], file_name[last_dot_index+1:]

def expandAllFromThisDir(input_dir, output_dir, videos_extensions, frames_extension, threads):
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
	videos_paths = []
	copy_tasks = []
	print('looking for videos...')
	for root, dirs, files in os.walk(input_dir):
		for file in files:
			name, extension = splitToNameAndExtension(file)
			if extension in videos_extensions:
				dir_for_frames_path = os.path.normcase(root.replace(input_dir, output_dir) + '/' + name)
				videos_paths.append((os.path.normcase(root + '/' + file), dir_for_frames_path))
			else:
				new_file_path = os.path.normcase(root.replace(input_dir, output_dir) + '/' + file)
				copy_tasks.append((os.path.normcase(root + '/' + file), new_file_path))
	print('found', len(videos_paths), 'videos')
	for result in tqdm(ThreadPool(threads).imap_unordered(lambda p: expandVideo(p[0], p[1], frames_extension), videos_paths), desc='Expanding videos from ' + input_dir, total=len(videos_paths)):
		pass
	for task in copy_tasks:
		new_dir = os.path.dirname(task[1])
		if not os.path.exists(new_dir):
			os.makedirs(new_dir)
		copyfile(*task)

expandAllFromThisDir(input_dir, output_dir, ['mp4', 'avi'], 'jpg', threads)