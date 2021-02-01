import os
import cv2
from functools import reduce
from itertools import chain

from files import getFilePath
from video import *

class Frames:
	def __init__(self, file):
		self.file = file

	def __iter__(self):
		path_to_file = getFilePath(self.file)
		video = getVideo(path_to_file)
		self.frame_count = video['frameCount']
		video['video'].release()
		self.current_frame_no = 0
		return self

	def __next__(self):
		if self.current_frame_no == self.frame_count:
			raise StopIteration
		frame = {
			'type': 'frame',
			'number': self.current_frame_no,
			'name': self.file['name'],
			'extension': self.file['extension'],
			'dir': self.file['dir']
		}
		self.current_frame_no += 1
		return frame

class Objects:
	def __init__(self, files, extensions):
		self.extensions = extensions
		self.files = chain(*map(self.getObjects, filter(self.isCorrectFile, files)))
		self.files_names = {}

	def isCorrectFile(self, file):
		return file['extension'] in self.extensions;

	def getObjects(self, file):
		if file['extension'] in ['mp4', 'avi']:
			return Frames(file)
		else:
			return [{
				'type': 'image',
				'name': file['name'],
				'extension': file['extension'],
				'dir': file['dir']
			}]

	def __next__(self):
		return next(self.files)

	def __iter__(self):
		return self

def getObjectPath(object):
	if len(object['dir']) > 0:
		return os.path.normcase(object['dir'] + '/' + object['name'] + '.' + object['extension'])
	else:
		return os.path.normcase(object['name'] + '.' + object['extension'])

def readObject(object, method = 'cv2'):
	file_path = getObjectPath(object)
	# print(file_path, os.path.getsize(file_path) // 1024)
	result = None
	if object['type'] == 'image':
		result = cv2.imread(file_path)
	elif object['type'] == 'frame':
		video = getVideo(file_path)
		result = getFrame(video, object['number'])
		video['video'].release()
	# print('ok')
	return result