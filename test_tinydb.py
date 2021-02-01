from tinydb import TinyDB, Query
import json
import cProfile
import dataset

def experiment_tinydb(objects_number):
	db = TinyDB('db.json')
	for i in range(objects_number):
		new_object = {
			'a': i,
			'b': str(i / 2)
		}
		db.insert(new_object)

def experiment_raw(objects_number):
	db = []
	for i in range(objects_number):
		new_object = {
			'a': i,
			'b': str(i / 2)
		}
		db.append(new_object)
	with open('db.json', 'w') as db_file:
		json.dump(db, db_file)
	with open('db.json', 'r') as db_file:
		db = json.load(db_file)

class customDB():
	def __init__(self, file_path, rewrite=False):
		self.file_path = file_path
		if rewrite:
			with open(self.file_path, 'w') as db_file:
				json.dump([], db_file)

	def add_record(self, record):
		db = None
		with open(self.file_path, 'r') as db_file:
			db = json.load(db_file)
			db.append(record)
		with open(self.file_path, 'w') as db_file:
			json.dump(db, db_file)

def experiment_custom(objects_number):
	db = customDB('db.json', rewrite=True)
	for i in range(objects_number):
		new_object = {
			'a': i,
			'b': str(i / 2)
		}
		db.add_record(new_object)

def experiment_dataset_write(objects_number):
	db = dataset.connect('sqlite:///db.db')
	table = db['sometable']
	for i in range(objects_number):
		new_object = {
			'a': i,
			'b': str(i / 2)
		}
		table.insert(new_object)

def experiment_dataset_query():
	db = dataset.connect('sqlite:///db.db')
	table = db['sometable']
	print(table.find_one(a=1))

def experiment_dataset_folded():
	db = dataset.connect('sqlite:///db.db')
	table = db['pairs']
	table.insert({
		'object': {
			'type': 'frame',
			'number': 28,
			'name': 'somename',
			'path': 'some/path',
			'extension': '.ext',
		},
		'annotations': [
			{
				'type': 'expr',
				'emotion': 3
			},
			{
				'type': 'VA',
				'valence': 0.4,
				'arousal': -0.9
			}
		]
	})

def experiment_rethinkdb_folded():
	from rethinkdb import RethinkDB
	r = RethinkDB()
	conn = r.connect(db='test')
	r.db_create('test_db').run(conn)
	r.db_list().run(conn)
	# db = dataset.connect('sqlite:///db.db')
	# table = db['pairs']
	# table.insert({
	# 	'object': {
	# 		'type': 'frame',
	# 		'number': 28,
	# 		'name': 'somename',
	# 		'path': 'some/path',
	# 		'extension': '.ext',
	# 	},
	# 	'annotations': [
	# 		{
	# 			'type': 'expr',
	# 			'emotion': 3
	# 		},
	# 		{
	# 			'type': 'VA',
	# 			'valence': 0.4,
	# 			'arousal': -0.9
	# 		}
	# 	]
	# })

# experiment_dataset_write(100)
# experiment_dataset_query()
# experiment_dataset_folded()
experiment_rethinkdb_folded()