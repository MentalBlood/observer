import json
import os
from convert_to_json_serializable import convert_to_json_serializable
from json_tools import *

class Report():
	def __init__(self, file_path, overwrite=True):
		self.file_path = file_path
		if overwrite:
			self.report = {}
		else:
			if os.path.exists(file_path):
				self.report = load_json_from_file(file_path)
			else:
				self.report = {}

	def write(self, name, value, dump_now=True):
		self.report[name] = value
		if dump_now:
			self.dump()

	def dump(self):
		print('dumping report to', self.file_path, '...')
		with open(self.file_path, 'w') as file:
			json.dump(self.report, file, default = convert_to_json_serializable, indent=4)

	def get(self):
		return self.report