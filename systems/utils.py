import re
from collections import defaultdict
import json
from nltk.corpus import stopwords
import pickle

########## FUNCTIONS RELATED TO COREFERENCE PROCESSING #########################

def get_sentence_offsets(doc):
    """Get a list of (start, end) offsets of the sentence documents."""
    sent_offsets=[]
    for s in doc.sents:
        sent_offsets.append(tuple([s.start_char, s.end_char]))
    return sent_offsets

def stringify_cluster_mentions(mentions):
    """Prepare a list of text values for a cluster, based on a list of mention objects."""
    stringy=[]
    for m in mentions:
        stringy.append(m.text)
    return stringy

def get_people_spans(names, text):
    """Obtain the occurences of the people names."""
    spans=defaultdict(list)
    for name in names:
        oc=[[m.start(),m.end()] for m in re.finditer(re.escape(name), text)]
        spans[name]=oc
    return spans

def get_coref_spans(names, text, doc):
    """Process the file with coreference relations."""
    
    people_spans=get_people_spans(names, text)
    
    spans=defaultdict(list)

    if not doc._.has_coref:
        return people_spans, spans, None

    clusters=doc._.coref_clusters
    for c in clusters:
        mentions=stringify_cluster_mentions(c.mentions)
        for person_name in names:
            if person_name in mentions:
                for m in c.mentions:
                    oc=[m.start_char, m.end_char]
                    if oc not in spans[person_name] and oc not in people_spans[person_name]:
                        spans[person_name].append(oc)
    return people_spans, spans, clusters

################### SEMEVAL DATA PREPARATION ##########################

def conll_to_text(rows):
    """Extract document text from its conll representation."""
    tokens=[]
    for row in rows:
        elements=row.split('\t')
#        print(elements, elements[1])
        if elements[1]=='NEWLINE':
            elements[1]='\n'
        tokens.append(elements[1])
    text=' '.join(tokens)
    return text

def load_text_from_json(filename):
    """Load text from a structured JSON file with three fields: DCT, title, and content."""
    data=load_json(filename)
    
    all_text = '%s\n%s\n%s' % (data['dct'], data['title'], data['content'])
    
    return all_text

def get_names(part_data):
    """Return the names of people given their annotation JSON."""
    names=[]
    for part_id, part_info in part_data.items():
        if 'Name' in part_info.keys() and part_info['Name'].strip():
            names.append(part_info['Name'].strip())
    return names

def transform_part_info(data):
    """Transform the participants annotation JSON, into one that has names as keys."""
    new_data={}
    for part_id, part in data.items():
        if 'Name' in part and part['Name'].strip():
            name=part['Name'].strip()
            new_part={}
            for k,v in part.items():
                if k.strip()=='Name': continue

                k=k.strip().lower()
                new_part[k]=v.strip().lower()
                if k=='ethnicity':
                    print(new_part[k], part_id)
            new_data[name]=new_part
    return new_data

def map_age_to_group(sys_data):
    for doc in sys_data:
        for part, data in doc.items():
            if 'age' in data:
                age=int(data['age'])
                age_group=None
                if age<12:
                    age_group='child 0-11'
                elif age<18:
                    age_group='teen 12-17'
                elif age<65:
                    age_group='adult 18-64'
                else:
                    age_group='senior 65+'
                data['age']=age_group
    return sys_data

################### OTHER HELPER FUNCTIONS ############################

def remove_stopwords(a_dict):
    """Remove the keys in a dictionary which are stopwords."""
    new_dict={}
    en_stopwords=set(stopwords.words('english'))
    for k, v in a_dict.items():
        if k not in en_stopwords:
            new_dict[k]=v
    return new_dict

def load_json(file):
    with open (file, 'r') as f:
        resources=json.load(f)
    return resources

def load_pickle(file):
    with open(file, 'rb') as tf:
        resources=pickle.load(tf)
    return resources

def dump_pickle(data, filename):
    with open(filename, 'wb') as wp:
        pickle.dump(data, wp)
    return

def get_sentence(span, sentence_offsets):
    for i, offset in enumerate(sentence_offsets):
        if span<offset[0]:
            break
    return i

def check_if_best_option(ps, attr_span, min_dist, closest_person, sentence_offsets, name):
    if get_sentence(ps[0], sentence_offsets)!=get_sentence(attr_span[0], sentence_offsets):
        return min_dist, closest_person
    if ps[0]<attr_span[0]: # person mentioned before the attribute
        dist=attr_span[0]-ps[1]
    else: # person mentioned after the attribute
        dist=ps[0]-attr_span[1]
    if dist<min_dist:
        min_dist=dist
        closest_person=name
    return min_dist, closest_person

def find_closest_person(attr_span, people_spans, coref_spans, sentence_offsets, min_dist=10):
    """Find the closest person to an attribute value."""
    closest_person=None
    for name, person_spans in people_spans.items():
        for ps in person_spans:
            # make sure to exclude cases where the attribute and the name overlap
            if (ps[0]<=attr_span[0] and ps[1]>=attr_span[1]) or (attr_span[0]<=ps[0] and attr_span[1]>=ps[1]):
                continue
            min_dist, closest_person=check_if_best_option(ps, attr_span, min_dist, closest_person, sentence_offsets, name)
    for name, c_spans in coref_spans.items():
        for cs in c_spans:
            min_dist, closest_person=check_if_best_option(cs, attr_span, min_dist, closest_person, sentence_offsets, name)
    return closest_person, min_dist

def get_closest_value_per_person(pairs):
    """Find the closest attribute value per person."""
    clean_pairs={}
    for person, person_pairs in pairs.items():
        clean_pairs[person]=sorted(person_pairs)[0][1]
    return clean_pairs

def lookup_person_in_list(name, ments):
    """Lookup a person in a list of strings as a partial match."""
    for m in ments:
        if name in m:
            return True
    return False

def count_per_attribute(rows):
    count_per_attr=defaultdict(int)
    for row in rows:
        for part, data in row.items():
            for attr in data.keys():
                count_per_attr[attr]+=1
    return count_per_attr

############## FUNCTIONS RELATED TO EVALUATION #######################################

def singularize_data(extractors_json):
    """Combine the information from the separate extractors."""
    result=defaultdict(dict)
    for attribute, extracted in extractors_json.items():
        for name, value in extracted.items():
            result[name][attribute]=value.lower()
    return dict(result)

def get_participant_info(data, sections=['shooter-section', 'victim-section']):
    """Obtain participant information with respect to several properties. This is used for evaluation purposes."""
    part_info={}
    for s in sections:
        for participant in data[s]:
            if participant['name']['value']:
                name=participant['name']['value'].strip()
                if name in part_info:
                    continue
                info={}
                if participant['gender']:
                    info['gender']=participant['gender'].lower().strip() # normalize for comparison
                    info['gender']=re.sub(r'\W+', '', info['gender'])
                if participant['age']['value']:
                    info['age']=participant['age']['value'].split('-')[0].strip() # to remove '-years-old
                    info['age']=re.sub(r'\W+', '', info['age'])
                if participant['race']['value']:
                    info['race']=participant['race']['value'].lower().strip() # to be normalized <TODO>
                    info['race']=re.sub(r'\W+', '', info['race'])
                part_info[name]=info
    return part_info

def benchmark_extractors(system, gold, attributes, debug=None):
    """Perform evaluation of system output."""
    assert len(system)==len(gold)
    tp=defaultdict(int)
    fp=defaultdict(int)
    fn=defaultdict(int)
    
    
    for index, gold_row in enumerate(gold):
        system_row=system[index]
        
        for part, gold_vals in gold_row.items():
            try:
                system_vals=system_row[part]
            except KeyError:
                system_vals={}
            
            for a in attributes:
                gold_val=''
                system_val=''
                if a in gold_vals:
                    gold_val=gold_vals[a].strip()
                if a in system_vals:
                    system_val=system_vals[a].strip()
                if gold_val and system_val:
                    if a==debug:
                        print(index, 'gold', gold_val, 'sys', system_val)
                    if gold_val==system_val:
                        tp[a]+=1
                    else:
                        fp[a]+=1
                        fn[a]+=1
                elif gold_val:
                    fn[a]+=1
                    if a==debug:
                        print(index, 'gold', gold_val)
                elif system_val:
                    fp[a]+=1
                    if a==debug:
                        print(index, 'sys', system_val)

    recall={}
    prec={}
    f1={}
    
    print(tp,fp, fn)
    for a in attributes:
        prec[a]=tp[a]/(tp[a]+fp[a])
        recall[a]=tp[a]/(tp[a]+fn[a])
        if prec[a]+recall[a]:
            f1[a]=2*prec[a]*recall[a]/(prec[a]+recall[a])
        else:
            f1[a]=0.0
    return prec, recall, f1
