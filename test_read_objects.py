from objects import readObject
import cv2
import cProfile

frame_data = {
	'type': 'frame',
	'number': 0,
	'name': '118-30-640x480',
	'extension': 'mp4',
	'dir': '../aff-wild2/expr/videos/validation_set'
}

frame = readObject(frame_data)
cv2.imwrite('image.jpg', frame)

image_data = {
	'type': 'image',
	'name': 'image',
	'extension': 'jpg',
	'dir': ''
}

def readFrames(number):
	for i in range(number):
		readObject(frame_data)

def readImages(number):
	for i in range(number):
		object = readObject(image_data)

cProfile.run('readFrames(100)')
cProfile.run('readImages(100)')