import csv
from json_tools import save_as_json, load_json_from_file
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description='Parse dataset and save pairs object-annotations')
parser.add_argument('--input', type=str,
                    help='csv file path', default=None)
parser.add_argument('--output', type=str,
                    help='links json file path', default=None)
args = parser.parse_args()

input_path = args.input
output_path = args.output

labels = ['medical_mask', 'not_medical_mask', 'no_mask']
def getLinksAndData(file_path):
	links_and_data = {}
	with open(file_path) as file:
		reader = csv.reader(file)
		for row in tqdm(reader):
			for element in row:
				if len(element) > 0:
					if element[0] == 'h':
						for l in labels:
							if l in row:
								links_and_data[element] = l
								break
	return links_and_data

links = getLinksAndData(input_path)
save_as_json(links, output_path)