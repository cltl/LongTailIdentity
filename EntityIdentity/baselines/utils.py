import re
from collections import defaultdict


########## FUNCTIONS RELATED TO COREFERENCE PROCESSING #########################

def get_sentence_offsets(doc):
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

################### OTHER HELPER FUNCTIONS ############################

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
