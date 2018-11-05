import json
import pickle
import argparse
import glob
from collections import defaultdict

NONAME='NONAME'

def transform_to_json(data):
    a_json = {}
    cluster_id=1
    for pid, separate_ids in data.items():
        for spid in separate_ids:
            a_json[spid]=cluster_id
        cluster_id+=1
    return a_json

if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser(description='Simple baseline based on people\'s full names.')
	parser.add_argument('-p', '--partition', required=True, type=str,
				help='On which data partition to run it: full or partial')
	args = vars(parser.parse_args())
	which_partition=args['partition']

	# set directories
	input_dir='../data/input/%s/annotation' % which_partition
	output_dir='../data/system/name_baseline/%s' % which_partition

	for input_file in glob.glob('%s/*' % input_dir):
		with open(input_file, 'rb') as f:
			group_by_name=defaultdict(set)
			input_data=pickle.load(f)
			for doc, docdata in input_data.items():
				#docdata=json.load(docdata)
				for part, participant in docdata.items():
					if 'Name' in participant.keys():
						name=participant['Name']
					else:
						name=NONAME
					group_by_name[name].add(part)
			system_json=transform_to_json(group_by_name)
		output_file='%s/%s.json' % (output_dir, (input_file.split('/')[-1]).split('.')[0])
		print(output_file)
		with open(output_file, 'w') as w:
			json.dump(system_json, w)
