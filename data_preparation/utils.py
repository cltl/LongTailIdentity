import pickle
from collections import OrderedDict

def get_all_names_set(participants_file_path):
    """ 
    Given the path of a file that contains all documents with their participants, 
    extract a set of all participant names
    """
    with open(participants_file_path, 'rb') as f:
        gva_input_annotations = pickle.load(f)
    all_names=set()
    for doc_id, data in gva_input_annotations.items():
        for participant_id, participant_info in data.items():
            if 'Name' in participant_info:
                all_names.add(participant_info['Name'])
    return all_names

def get_all_names_list(participants_file_path):
    """ 
    Given the path of a file that contains all documents with their participants, 
    extract a list of all participant names
    """
    with open(participants_file_path, 'rb') as f:
        gva_input_annotations = pickle.load(f)
    names_list=[]
    for doc_id, data in gva_input_annotations.items():
        for participant_id, participant_info in data.items():
            if 'Name' in participant_info:
                names_list.append(participant_info['Name'])
    return names_list

def load_conll_data(file_location):
    """
    Load the conll file data into a dictionary.
    """
    conll_data=OrderedDict()
    with open(file_location, 'r') as f:
        for line in f:
            if line.startswith('#begin'):
                docid=""
                list_of_lines=[]
                start_line=line
            elif line.startswith("#end"):
                end_line = line
                conll_data[docid]={
                    'dct': dct,
                    'content': list_of_lines,
                    'start_line': start_line,
                    'end_line': end_line
                }
            else:
                line_elements=line.split()
                if docid=="":
                    docid=line_elements[0].split('.')[0]
                if line_elements[2]=='DCT':
                    start_line+=line
                    dct=line_elements[1]
                else:
                    list_of_lines.append(line)
    return conll_data

def transform_gold_to_json(data, skip_empty=False, empty_names=set()):
    a_json = {}
    cluster_id=1
    for pid, separate_ids in data.items():
        for spid in separate_ids:
            increment=False
            if not skip_empty or spid not in empty_names:
                a_json[spid]=cluster_id
                increment=True
        if increment:
            cluster_id+=1
    return a_json

def create_ambiguous_data(input_file, output_file, new_name='', new_firstname='', new_lastname=''):
    with open(input_file, 'rb') as f:
        gva_input_annotations=pickle.load(f)
    for doc_id, data in gva_input_annotations.items():
        for participant_id, participant_info in data.items():
            if 'Name' in participant_info and participant_info['Name'].strip():
                old_name=participant_info['Name'].strip()
                if new_name:
                    participant_info['Name']=new_name
                elif new_firstname:
                    first_name, *other_names = old_name.split()
                    participant_info['Name']=' '.join([new_firstname] + other_names)
                elif new_lastname:
                    *other_names, last_name = old_name.split()
                    participant_info['Name']=' '.join(other_names + [new_lastname])
                else:
                    return

    with open(output_file, 'wb') as w:
        pickle.dump(gva_input_annotations, w)
        
    return

def load_pickle(file):
    with open(file, 'rb') as tf:
        resources=pickle.load(tf)
    return resources
