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

def decide_merging(data):
    keys_to_keep=[]
    merged={}
    for combination in data:
        for combination2 in data:
            if combination>combination2:
                to_merge=True
                new_key=[]
                for key_pos in range(0,len(combination)):
                    if combination[key_pos]!=combination2[key_pos] and combination[key_pos] and combination2[key_pos]:
                        to_merge=False
                        break
                    elif combination[key_pos]:
                        new_key.append(combination[key_pos])
                    else:
                        new_key.append(combination2[key_pos])
                if to_merge:
                    tuple_key=tuple(new_key)
                    merged[tuple(combination)]=tuple_key
                    merged[tuple(combination2)]=tuple_key
    return merged

def create_keys_per_name(data):
    keys_per_name=defaultdict(list)
    for key, ids in data.items():
        name, *rest=key
        keys_per_name[name].append(rest)
    return keys_per_name

def perform_merging(data):
    new_data=defaultdict(set)

    keys_per_name = create_keys_per_name(data)
    for name, vals in keys_per_name.items():
        if len(vals)>1:
            merged_vals=decide_merging(vals)
            for v in vals:
                if tuple(v) in merged_vals.keys():
                    new_key=tuple([name] + list(merged_vals[tuple(v)]))
                    test_key=tuple([name] + v)
                    the_value=data[test_key]
                    new_data[new_key] |= the_value
                else:
                    new_key=tuple([name] + v)
                    new_data[new_key] |= data[new_key]
        else:
            test_key=tuple([name] + vals[0])
            the_value=data[test_key]
            new_data[test_key]=the_value
    return new_data

def count_values(data):
	s=0
	for k,v in data.items():
		s+=len(v)
	return s

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

	# Define which properties to consider
	properties=['Name']
#	properties+=['CauseOfDeath', 'EducationLevel', 'Residence']
#	properties+=['Residence', 'Religion', 'Ethnicity']
	properties+=['CauseOfDeath', 'EducationLevel', 'Residence', 'Religion', 'Ethnicity', 'PastConviction' , 'BirthPlace'] # 
	properties+=['Gender', 'Age', 'DeathDate', 'DeathPlace']
#	properties+=['Age', 'Gender']
#	properties+=['Age']

	for input_file in glob.glob('%s/*' % input_dir):
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
		new_data=perform_merging(group_by_name_plus)
		system_json=transform_to_json(new_data)
		output_file='%s/%s.json' % (output_dir, (input_file.split('/')[-1]).split('.')[0])
		with open(output_file, 'w') as w:
			json.dump(system_json, w)
