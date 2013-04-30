import pyoracle
import random
import numpy as np

from matplotlib.mlab import find

oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}
s = [1] # current point for nav
k = 1 # starting point for nav
p = 0.5 # jump probability 

thresh = 0.1
lrs = 0

weights = {'mfcc': 1.0,
           'centroid': 0.0,
           'amp': 0.0,
           'pitch': 0.0,
           'zerocrossings': 0.0}

region = {'start': 0.0, 'end': 1.0}
start = 0
end = 1
regions_active = 0

def set_region(s, e):
    global region, start, end
    region['start'] = s
    region['end'] = e
    start = int(len(oracle['lrs'])*region['start'])
    end = int(len(oracle['lrs'])*region['end'])
    if end <= start:
        end = start + 5

def toggle_regions(tog):
    global regions_active
    regions_active = tog

def set_threshold(new_thresh):
    global thresh
    thresh = new_thresh

def start_oracle():
    global oracle,k,s, region,lrs
    s = [1]
    k = 1
    oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}
    pyoracle.Resources.PyOracle.PyOracle.add_initial_state(oracle) 
    region = {'start': 0.0, 'end': 1.0}
    # lrs =0

def begin():
    global oracle
    start_oracle()
    return "Oracle Initialized"

def add_new_state(m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,centroid,amp,zc,pitch,time):
    global oracle, thresh
    new_event = {}
    mfccs = []
    mfccs.append(m1)
    mfccs.append(m2)
    mfccs.append(m3)
    mfccs.append(m4)
    mfccs.append(m5)
    mfccs.append(m6)
    mfccs.append(m7)
    mfccs.append(m8)
    mfccs.append(m9)
    mfccs.append(m10)
    new_event['mfcc'] = mfccs
    new_event['time'] = time

    new_event['amp'] = amp
    new_event['zerocrossings'] = zc
    new_event['pitch'] = pitch
    new_event['centroid'] = centroid

    pyoracle.Resources.PyOracle.PyOracle.add_state(oracle, new_event, thresh, weights)
    
    return 'n_states', len(oracle['lrs'])

def dump_oracle():
    global oracle
    print 'transitions:', str(oracle['trn'])
    print 'suffixes:', str(oracle['sfx'])
    print 'rev. suffixes:', str(oracle['rsfx'])
    print 'lrs:', str(oracle['lrs'])

def set_probability(new_p):
    global p
    p = new_p

def set_lrs(new_lrs):
    global lrs
    lrs = new_lrs

def get_ir():
    global oracle
    IR, code, compror = pyoracle.calculate_ir(oracle)
    '''
    ir_list = []
    for i in IR[1]:
        ir_list.append(i)
    return 'ir', str(ir_list)[1:-2].replace(',', '')
    '''
    return 'ir', float(IR[1].sum())

def get_next_state():
    '''
    generate output state from audio oracle
    outputs:
        k - value of next state
    '''
    global s, k,p, lrs, start, end, regions_active

    ktrace = [1]
    in_region = False

    # these should be globals which are set elsewhere
    # so regions don't change dynamically with the oracle size
    # start = int(len(oracle)*region['start'])
    # end = int(len(oracle)*region['end'])
    
    # forward transition or jump

    if (random.random() < p) and k < len(oracle['lrs']) - 1:
        # transition
        k += 1
    else:
        # maybe look more into 'navigating the oracle paper'
        # suffix
        options = [oracle['sfx'][k]]
        # rev sfx
        options.append(oracle['rsfx'][k])
        # suffix of suffix
        options.append(oracle['sfx'][oracle['sfx'][k]])
        # rsfx of rsfx
        if type(oracle['rsfx'][k]) == int:
            # single val
            options.append(oracle['rsfx'][oracle['rsfx'][k]])
        else:
            # list
            options.append([oracle['rsfx'][rs] for rs in oracle['rsfx'][k]])

        options = filter(lambda x: type(x) == int, options)
        options = filter(lambda x: oracle['lrs'][x] >= lrs, options) 
        try:
            k = sorted(options, key = lambda x: oracle['lrs'][x])[-1]
            # but if we jump back to zero, choose a new state
            if k == 0:
                k = random.choice(oracle['trn'][0])
        except:
            # if no good jump, then step forward
            k += 1

    # if k is out of region
    num_iterations = 0
    iteration_limit = 40
    while start > k or k > end and regions_active:
        if num_iterations > iteration_limit:
            print 'reached max iterations'
            return 'next_state', random.choice(range(start, end))
        num_iterations += 1
        print 'start:', start, 'k:', k, 'end:', end
        # do another suffix jump
        options = [oracle['sfx'][k]]                        
        # rev sfx
        options.append(oracle['rsfx'][k])
        # suffix of suffix
        options.append(oracle['sfx'][oracle['sfx'][k]])
        # rsfx of rsfx
        # print k
        # options.append([oracle['rsfx'][rs] for rs in oracle['rsfx'][k]])
                                                            
        options = filter(lambda x: type(x) == int, options)
        for opt in options:
            if start <= opt <= end:
                k = opt
                return 'next_state', k            
        # if no good option found, jump back along suffix
        # could also jump forward if we're behind the region
        k = oracle['sfx'][k]
        if k == 0:
            k = random.choice(oracle['trn'][0])
    return 'next_state', k
