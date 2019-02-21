#!/usr/bin/env python
# coding: utf-8

# Import standard libraries
import glob
import pickle
from collections import defaultdict
import json
import pandas as pd

# Import custom libraries
import utils

property_set='p10'
partitions=['partial', 'full']
extractors=['gold', 'auto']
datasets=['PD1', 'PD2', 'PD3', 'PD4', 'FD1', 'FD2', 'FD3', 'FD4']

def get_num_unique_combos(data_dir, keys):
    """
    Get number of occurrences for a property combination.
    """
    for input_file in glob.glob('%s/*.*' % data_dir):
        with open(input_file, 'rb') as f:
            data=pickle.load(f)
            grouped_by_props=defaultdict(list)
            for doc_id, doc_data in data.items():
                for part_id, part_props in doc_data.items():
                    k=utils.create_key(part_props, keys)
                    grouped_by_props[k].append(part_id)
        print(input_file)
        print('Number of unique combinations:', len(grouped_by_props.keys()))
        print('Distribution', json.dumps(utils.get_distribution(grouped_by_props), sort_keys=True))
        
def analyze_distinguishability_of_props(data_dir, keys):
    """
    Analyze how often can two entity pairs be distinguished based on properties, and splits this into: distinguishable, indistinguishable, and sufficient to distinguish.
    """
    input_sets={}
    for input_file in glob.glob('%s/*.*' % data_dir):
        with open(input_file, 'rb') as f:
            data=pickle.load(f)
            grouped_by_name=defaultdict(dict)
            for doc_id, doc_data in data.items():
                for part_id, part_props in doc_data.items():
                    if 'Name' not in part_props.keys() or not part_props['Name'].strip(): continue
                    name=part_props['Name'].strip()
                    k=utils.create_key(part_props, keys)
                    grouped_by_name[name][part_id]=k
        #print(input_file)
        filename=utils.get_filename(input_file)
        input_sets[filename]=utils.obtain_sets(grouped_by_name)
        
    return input_sets

def print_stars():
    """
    Print many star signs for better visual separation of output. 
    """
    print('*'*75)

def print_tables(all_data):
    """
    Print all tables based on a dictionary data.
    """
    for aspect, data in all_data.items():
        if not data: continue
        print()
        print(aspect)
        df_input=pd.DataFrame.from_dict(data)
        print(df_input.columns)
        df_input=df_input[datasets]
        df_input=df_input.fillna('-')
        print(df_input.to_csv(sep='\t'))
    
def main(extractor, unique_combos_analysis, 
        input_data_analysis, input_gold_analysis, 
        input_system_gold_analysis):
    """
    Main analysis function - obtain results on the input data only, input in combination with gold output, and in combination with the system answers.
    """
    table_data={'input': defaultdict(dict), 
                'input_gold': defaultdict(dict),
                'system_gold': defaultdict(dict)}

    for partition in partitions:
#    for partition in ['partial']:

        # Setup directories
        #input files
        gold_prop_dir='../data/input/%s/annotation' % partition
        auto_prop_dir='../systems/extracted_data/%s' % partition

        # load gold file
        gold_file='../data/gold/%s/participants.json' % partition
        with open (gold_file, 'rb') as gf:
            gold_data=json.load(gf)

        # system files
        baseline_dir='../data/system/%s/%s' % (extractor, partition)
        profiler_dir='../data/system/%s_profiling/%s' % (extractor, partition)

        # load system data
        sys_data={}
        for bdir in glob.glob('%s/*' % baseline_dir):
            b=utils.get_filename(bdir)
            ext_baseline_dir='%s/%s' % (bdir, property_set)
            sys_data[b]=utils.load_system_datasets(ext_baseline_dir)
        sys_data['profiler']=utils.load_system_datasets(profiler_dir)

        # define input dir and property set
        if extractor=='gold':
            data_dir=gold_prop_dir
            keys=['Ethnicity', 'Gender', 'Age', 'Religion', 'CauseOfDeath',
              'Occupation']
        else:
            data_dir=auto_prop_dir
            keys=['Residence', 'Ethnicity', 'EducationLevel', 'MedicalCondition', 
              'BirthPlace', 'Gender', 'Age', 'Religion', 'PastConviction',
              'CauseOfDeath', 'DeathPlace', 'DeathDate', 'Name']



        # 1. Analyze numbers of local contexts with unique properties
        if unique_combos_analysis:
            print_stars()
            get_num_unique_combos(data_dir, keys)
            print_stars()


        input_sets=analyze_distinguishability_of_props(data_dir, keys)
        # 2. Analyze distinguishability of properties
        if input_data_analysis:
            for filename, sets in input_sets.items():
                dataset=utils.map_filename(filename, partition)
                if not dataset: continue
                for k, v in sets.items():
                    data_part=k.replace('set_', '')
                    table_data['input'][dataset][data_part]=len(v)
                prof_perc=round(len(sets['set_profiler'])*100/len(sets['set_total']))
                table_data['input'][dataset]['profiler %']=prof_perc

        # 3. Analyze distribution of sameness in each of the distinguishability sets
        if input_gold_analysis:
            for filename, sets in input_sets.items():
                dataset=utils.map_filename(filename, partition)
                if not dataset: continue
                for set_name, the_set in sets.items():
                    same, different=utils.analyze_performance_on_pairs(the_set, 
                                                                       gold_data)
                   
                    k1=(set_name.replace('set_', ''), 'same')
                    table_data['input_gold'][dataset][k1]=same
                    k2=(set_name.replace('set_', ''), 'different')
                    table_data['input_gold'][dataset][k2]=different

        # 4. Analyze system performance on each of the sets
        if input_system_gold_analysis:
            print_stars()
            for s, sdata in sys_data.items():
                for filename, sets in input_sets.items():
                    if filename not in sdata.keys(): 
                        continue
                    dataset=utils.map_filename(filename, partition)
                    if not dataset: continue
                        
                    sys_predictions=sdata[filename]
                    for set_name, the_set in sets.items():
                        acc_counts, total_counts=utils.scores_vs_identity(gold_data,
                                                            sys_predictions, the_set)
                        gold_same_acc=utils.compute_acc(acc_counts, total_counts,
                                                            gold_same=True)
                        gold_diff_acc=utils.compute_acc(acc_counts, total_counts, 
                                                            gold_same=False)
                        
                        k1=(set_name.replace('set_', ''), s, 'same')
                        table_data['system_gold'][dataset][k1]=round(gold_same_acc, 2)
                        k2=(set_name.replace('set_', ''), s, 'different')
                        table_data['system_gold'][dataset][k2]=round(gold_diff_acc, 2)
                print_stars()    

    print_tables(table_data)
    
if __name__ == "__main__":

    unique_combos_analysis=False
    input_data_analysis=True
    input_gold_analysis=True
    input_system_gold_analysis=True
    
    for extractor in extractors:
        print_stars()
        print(extractor)
        main(extractor, unique_combos_analysis, 
            input_data_analysis, input_gold_analysis, 
            input_system_gold_analysis)
        print_stars()
