import json
from collections import defaultdict
import random

def transform_to_json(data):
    a_json = {}
    cluster_id=1
    for pid, separate_ids in data.items():
        for spid in separate_ids:
            a_json[spid]=cluster_id
        cluster_id+=1
    return a_json

def create_keys_per_name(data):
    """
    Get dictionary where keys are property combinations and values are local IDs. 
    Return data where the keys are names, whereas the values are dictionaries (properties, ids).
    """
    keys_per_name={}
    for key, ids in data.items():
        name, *rest=key
        key_tuple=tuple(key)
        if name not in keys_per_name.keys():
            keys_per_name[name]=defaultdict(set)
        keys_per_name[name][key_tuple]=ids
    return keys_per_name

def decide_merging(combinations):
    """
    Given all local contexts for a name, decide which of them to merge. We do this by comparing property value lists. 
    """
    merged={}
    for combination in combinations: # list of lists
        for combination2 in combinations:
            if combination>combination2:
                # first check if this combination has already been merged
                if tuple(combination) in merged.keys():
                    combination=merged[tuple(combination)]
                if tuple(combination2) in merged.keys():
                    combination2=merged[tuple(combination2)]
                    
                # now decide on merging!
                to_merge=True # merge by default except if you find a clashing property
                new_key=[]
                for key_pos in range(0,len(combination)): # if there is a clash, then set to_merge to False 
                    if combination[key_pos]!=combination2[key_pos] and combination[key_pos] and combination2[key_pos]: # clash means two non-empty values are different
                        to_merge=False
                        break
                    elif combination[key_pos]: # store the property value if there is no clash, whichever combination has it
                        new_key.append(combination[key_pos])
                    else: # store the property value if there is no clash, whichever combination has it
                        new_key.append(combination2[key_pos])
                        
                # if we merge these two, then assign each of them to the superior combination of property values
                if to_merge:
                    merged[tuple(combination)]=tuple(new_key)
                    merged[tuple(combination2)]=tuple(new_key)
    return merged

def lookup_key(d, test_key):
    """
    For debugging: Check whether a key exists among the IDs.
    """
    for n, vals in d.items():
        for v, ids in vals.items():
            if test_key in ids: 
                print(test_key, n, len(vals))
                return True
    return False
            
def perform_merging(keys_per_name):
    """
    Perform clustering between the local contexts for all names.
    """
    
    new_data=defaultdict(set)
    
    for name, prop_vals in keys_per_name.items(): # Iterate over all names
        prop_combinations=list(prop_vals.keys())
        random.shuffle(prop_combinations)
        merged_vals=decide_merging(prop_combinations)
        for values, ids in prop_vals.items():
            values_tuple=tuple(values)

            if values_tuple in merged_vals.keys(): # if these values are to be merged, then get their new/extended set of properties
                new_key=tuple([name] + list(merged_vals[values_tuple]))
                new_data[new_key] |= ids
            else:
                new_data[values_tuple] |= ids

    return new_data

def count_values(data):
	s=0
	for k,v in data.items():
		s+=len(v)
	return s
