from cluster_utils import decide_merging as merge
import random

lc1=('', 'black', 'male')
lc2=('', '', 'female')
lc3=('christian', '', '')
lc4=('christian', '', 'female')

data=[lc2, lc1, lc3, lc4]

random.shuffle(data)

m=merge(data)
print(m)
