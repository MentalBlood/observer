import cv2
import cProfile

# video_path = '..\\aff-wild2\\expr\\videos\\validation_set\\118-30-640x480.mp4'
video_path = '..\\aff-wild2\\expr\\videos\\validation_set\\121-24-1920x1080.mp4'
frames_dir = 'frames_1920x1080'

def expandVideo(video_path, frames_dir):
	video = cv2.VideoCapture(video_path)
	frame_number = 0
	while True:
		frame = video.read()
		if not frame[0]:
			break
		cv2.imwrite(frames_dir + '\\' + str(frame_number) + '.png', frame[1])
		frame_number += 1
	print(frame_number)

cProfile.run('expandVideo(video_path, frames_dir)')

# png: 7.72MB -> 856MB (x110)
# jpg: 7.72MB -> 153MB (x20)

# 2420x640x480, png: 26.3sec total, 24.7sec writing
# 10628x1920x1080, png: 561sec total, 491sec writing