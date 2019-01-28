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
    
	parser.add_argument('-e', '--extractor', required=True, type=str,
                                help='Which extractor to use: gold or auto')
    
	args = vars(parser.parse_args())
	which_partition=args['partition']
	which_extractor=args['extractor']

	# set directories
	if which_extractor=='gold':
            input_dir='../data/input/%s/annotation' % which_partition
            output_dir='../data/system/name_students_baseline/%s' % which_partition
	else:
            input_dir='extracted_data/%s' % which_partition
            output_dir='../data/system/auto_ext_baseline/%s' % which_partition
        
        
	print(input_dir, output_dir)
    
	# Define which properties to consider
	properties=['Name']
	properties+=['Residence', 'Religion', 'Ethnicity']
	properties+=['CauseOfDeath', 'EducationLevel', 'Residence', 'Religion', 'Ethnicity', 'PastConviction', 'BirthPlace'] # 
	properties+=['Gender', 'AgeGroup', 'DeathDate']
	properties+=['Age']

	for input_file in glob.glob('%s/*' % input_dir):
		print(input_file)
		with open(input_file, 'rb') as f:
			group_by_name_plus=defaultdict(set)
			input_data=pickle.load(f)
			for doc, docdata in input_data.items():
				for part, participant in docdata.items():
					tuple_key=[]
					for p in properties:
						if p in participant.keys():
							tuple_key.append(participant[p])
						else:
							tuple_key.append('')
					group_by_name_plus[tuple(tuple_key)].add(part)
			system_json=transform_to_json(group_by_name_plus)
		output_file='%s/%s.json' % (output_dir, (input_file.split('/')[-1]).split('.')[0])
		print(output_file)
		with open(output_file, 'w') as w:
			json.dump(system_json, w)
