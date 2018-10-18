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
