import json
import pickle
import argparse
import glob
from collections import defaultdict
import sys

import cluster_utils as cu

############## MAIN FUNCTION #################

def process_file_with_baseline(input_file, merger, properties, output_file):
    with open(input_file, 'rb') as f:
        group_by_prop_values=defaultdict(set)
        input_data=pickle.load(f)
        for doc, docdata in input_data.items():
            for part, participant in docdata.items():
                tuple_key=[]
                for p in properties:
                    if p in participant.keys():
                        tuple_key.append(participant[p])
                    else:
                        tuple_key.append('')
                group_by_prop_values[tuple(tuple_key)].add(part)
    print(len(group_by_prop_values.keys()))
    if merger=='exact':
        new_data=group_by_prop_values
    else: # 'noclash'
        keys_per_name = cu.create_keys_per_name(group_by_prop_values)
        new_data=cu.perform_merging(keys_per_name)
        if DEBUG:
            basename=(input_file.split('/')[-1]).split('.')[0]
            log_file_props='../logs/props_%s.json' % basename
            log_file_clusters='../logs/clusters_%s.json' % basename
    system_json=cu.transform_to_json(new_data)
    
    with open(output_file, 'w') as w:
        json.dump(system_json, w)

        
def perform_clustering(input_dir, merger, properties, output_dir):
    for input_file in glob.glob('%s/*' % input_dir):
        output_file='%s/%s.json' % (output_dir, (input_file.split('/')[-1]).split('.')[0])
        process_file_with_baseline(input_file, merger, properties, output_file)

if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser(description='Run clustering based on extracted properties.')

	parser.add_argument('-p', '--partition', required=True, type=str,
		help='On which data partition to run it: full or partial')
	parser.add_argument('-e', '--extractor', required=True, type=str,
                help='Which extractor to use: gold or auto')
	parser.add_argument('-m', '--merger', required=True, type=str,
                help='Which merger to use: exact or noclash')
	parser.add_argument('-c', '--combination', required=True, type=str,
                help='Which combination of properties: p0 (name only) - p10 - all properties')

	args = vars(parser.parse_args())
	which_partition=args['partition']
	which_extractor=args['extractor']
	merger=args['merger']
	which_combination=args['combination']
    
    DEBUG=True

	# set directories
	if which_extractor=='gold':
            input_dir='../data/input/%s/annotation' % which_partition
	else:
            input_dir='extracted_data/%s' % which_partition
	output_dir='../data/system/%s/%s/%s/%s' % (which_extractor, which_partition, merger, which_combination)

	# Define which properties to consider
	prop_combos = {'p0': ['Name'], 'p1': ['Name', 'CauseOfDeath', 'EducationLevel'], 'p2': ['Name', 'CauseOfDeath', 'EducationLevel', 'Residence'],
                       'p3': ['Name', 'CauseOfDeath', 'EducationLevel', 'Residence', 'Religion', 'Ethnicity', 'PastConviction'],
                       'p4': ['Name', 'CauseOfDeath', 'EducationLevel', 'Residence', 'Religion', 'Ethnicity', 'PastConviction', 'BirthPlace'],
                       'p5': ['Name', 'Age'],
                       'p6': ['Name', 'Age', 'Gender'],
                       'p7': ['Name', 'Age', 'Gender', 'DeathDate'],
                       'p8': ['Name', 'Age', 'Gender', 'DeathPlace'],
                       'p9': ['Name', 'Age', 'Gender', 'DeathDate', 'DeathPlace'],
#                       'p10': ['Name', 'AgeGroup', 'Gender', 'DeathDate'],
#                       'p11': ['Name', 'AgeGroup', 'Gender', 'DeathPlace'],
#                       'p12': ['Name', 'AgeGroup', 'Gender', 'DeathDate', 'DeathPlace'],
                       'all': ['Name', 'CauseOfDeath', 'EducationLevel', 'Residence', 'Religion', 'Ethnicity', 'PastConviction', 'BirthPlace', 'Age', 'Gender', 'DeathDate', 'DeathPlace'],
                       'p10': ['Name', 'CauseOfDeath', 'Religion', 'Ethnicity', 'Age', 'Gender']
                      }
	properties=prop_combos[which_combination]

	perform_clustering(input_dir, merger, properties, output_dir)
    
