import glob
from collections import defaultdict
import json

def create_key(props, keys):
    the_key=[]
    for k in keys:
        if k in props.keys():
            v=props[k].strip()
        else:
            v=''
        the_key.append(v)
    return tuple(the_key)


def get_distribution(data):
    counter=defaultdict(int)
    for k, v in data.items():
        counter[len(v)]+=1
    return counter

def get_filename(f):
    return f.split('/')[-1].split('.')[0]


def get_filename(f):
    return f.split('/')[-1].split('.')[0]

def obtain_sets(grouped_by_name):
    set_indistinguishable=set()
    set_distinguishable=set()
    set_sufficient=set()
    set_total=set()

    for name, parts in grouped_by_name.items():
        for p1, p1_data  in parts.items():
            for p2, p2_data in parts.items():
                if p1>p2:
                    pair=(p1,p2)
                    set_total.add(pair)
                    if p1_data==p2_data:
                        set_indistinguishable.add(pair)
                    else:
                        set_distinguishable.add(pair)
                        for index, e1 in enumerate(p1_data):
                            e2=p2_data[index]
                            if e1!=e2 and e1!='' and e2!='':
                                set_sufficient.add(pair)
                                break

    set_profiler=set_distinguishable-set_sufficient

    sets={'set_indistinguishable': set_indistinguishable, 
            'set_distinguishable': set_distinguishable, 
            'set_sufficient': set_sufficient,
            'set_profiler': set_profiler,
            'set_total': set_total}
    return sets

def load_system_datasets(the_dir):
    the_data={}
    #print(the_dir)
    for f in glob.glob('%s/*.*' % the_dir):
        with open(f, 'rb') as ff:
            #print(f)
            fname=f.split('/')[-1].split('.')[0]
            the_data[fname]=json.load(ff)
    return the_data

def analyze_performance_on_pairs(pairs, gold_data):
    """
    Analyze the how many of the (in)distinguishable pairs are the same
    """
    same=0
    different=0
    for id1,id2 in pairs:
        cluster_id1=gold_data[id1]
        cluster_id2=gold_data[id2]
        if cluster_id1==cluster_id2:
            same+=1
        else:
            different+=1
    return same, different


def get_decision(id1, id2, data):
    cluster_id1=data[id1]
    cluster_id2=data[id2]
    return cluster_id1==cluster_id2



def scores_vs_identity(gold_data, sys_data, pairs):
    """
    Analyze the system performance on the (in)distinguishable ones
    """
    acc_counts=defaultdict(int)
    total_counts=defaultdict(int)
    for id1,id2 in pairs:
        sys_same=get_decision(id1, id2, sys_data)
        gold_same=get_decision(id1, id2, gold_data)

        if sys_same==gold_same: # both have voted for the same decision
            acc_counts[(sys_same, gold_same)]+=1
        total_counts[gold_same]+=1
        
    return acc_counts, total_counts


def compute_acc(acc, total, gold_same=False):
    if total[gold_same]>0:
        return acc[(gold_same, gold_same)]*100.0/total[gold_same]
    else:
        return -1

def map_filename(f, partition):
    prefix=partition[0].upper()
    if f=='participants_input':
        return prefix + 'D1'
    elif f=='participants_samefirstname':
        return prefix + 'D2'
    elif f=='participants_samelastname':
        return prefix + 'D3'
    elif f=='participants_samename':
        return prefix + 'D4'
    else:
        return ''