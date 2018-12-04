# imports
import glob
import pickle
from sklearn.metrics.cluster import adjusted_rand_score
import utils
import json
import argparse

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser(description='Evaluate a clustering output.')
	parser.add_argument('-p', '--partition', required=True, type=str, 
				help='which partition: full or partial')
	parser.add_argument('-s', '--system_name', required=True, type=str, 
				help='which system to evaluate')
	args = vars(parser.parse_args())
	system_name=args['system_name']
	which_partition=args['partition']

	# Combine into directories
	gold_file = '../data/gold/%s/participants.json' % which_partition
	system_dir = '../data/system/%s/%s' % (system_name, which_partition)

	with open(gold_file, 'r') as g:
		gold_json = json.load(g)
    
	all_separate_participants=list(gold_json.keys())

	for system_file in glob.glob('%s/*.json' % system_dir):

		with open(system_file, 'r') as s:
			system_json = json.load(s)



		# From JSON to lists that can be used to evaluate on
		sys_list=[]
		gold_list=[]
		for spid in all_separate_participants:
			try:
			    sys_list.append(system_json[spid])
			except KeyError:
                            sys_list.append(-1)
			gold_list.append(gold_json[spid])

		score=adjusted_rand_score(gold_list, sys_list)

		print(system_file, score)

