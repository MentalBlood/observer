import os

def splitToNameAndExtension(file_name):
	last_dot_index = file_name.rfind('.')
	return file_name[:last_dot_index], file_name[last_dot_index+1:]

def getFiles(folder):
	result = []
	for root, dirs, files in os.walk(folder):
		for file in files:
			name, extension = splitToNameAndExtension(file)
			result.append({
				'name': name,
				'extension': extension,
				'dir': os.path.normpath(root)
			})
	return result

def getFilePath(file):
	return os.path.normcase(file['dir'] + '/' + file['name'] + '.' + file['extension'])