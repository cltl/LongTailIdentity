import json
from collections import defaultdict

def transform_to_json(data):
    a_json = {}
    cluster_id=1
    for pid, separate_ids in data.items():
        for spid in separate_ids:
            a_json[spid]=cluster_id
        cluster_id+=1
    return a_json

def decide_merging(data):
    merged={}
    for combination in data:
        for combination2 in data:
            if combination>combination2:
                if tuple(combination) in merged.keys():
                    combination=list(merged[tuple(combination)])
                if tuple(combination2) in merged.keys():
                    combination2=list(merged[tuple(combination2)])
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
