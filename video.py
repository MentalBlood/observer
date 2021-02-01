import cv2

def getVideo(path):
	video = cv2.VideoCapture(path)
	return {
		'video': video,
		'frameCount': int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
		'width': int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
		'height': int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
	}

def setCurrentFrame(video, frameNo):
	video['video'].set(1, frameNo)

def getCurrentFrame(video):
	return video['video'].read()[1]

def getFrame(video, frameNo):
	setCurrentFrame(video, frameNo)
	return getCurrentFrame(video)