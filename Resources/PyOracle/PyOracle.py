#############################################################################
# pyoracle.py 
# builds a factor oracle from an input string of audio features
# modified 09.18.2012
# greg surges
# copyleft 2011 - 2012
#############################################################################

import time

import State
from random import randint
from itertools import izip

oracle = []
features = ['mfcc', 'centroid', 'rms', 'chroma', 'zerocrossings']
#############################################################################
# ORACLE CONSTRUCTION FUNCTIONS
#############################################################################

def get_distance(event1, event2, weights = None):
    """
    get distance between frames 
    """
    if weights == None:
        weights = {'mfcc': 1.0,            
                   'centroid': 1.0,
                   'rms': 1.0,
                   'chroma': 1.0,
                   'zerocrossings': 1.0}
    
    mfccs = izip(event1['mfcc'], event2['mfcc'])
    mfccs = sum((a - b) * (a - b) for a, b in mfccs) / 38
    mfccs *= weights['mfcc']

    chroma = izip(event1['chroma'], event2['chroma'])
    chroma = sum((a - b) * (a - b) for a, b in chroma) / 12
    chroma *= weights['chroma']
    
    centroid = ((event1['centroid'] - event2['centroid']) 
                * (event1['centroid'] - event2['centroid'])
                * weights['centroid'])

    rms = ((event1['rms'] - event2['rms']) 
            * (event1['rms'] - event2['rms'])
            * weights['rms'])

    zerocrossings = ((event1['zerocrossings'] - event2['zerocrossings']) 
            * (event1['zerocrossings'] - event2['zerocrossings'])
            * weights['zerocrossings'])

    return mfccs + centroid + rms + chroma + zerocrossings 

def add_initial_state(states):
    states.append(State.State(0))

def add_state(states, new_data, threshold = 0, weights = None):
    # create a new state numbered i
    new_state = State.State(len(states))
    # print 'added new state:', new_state.number
    states.append(new_state) 
    # assign a new transition from state i - 1 to state i
    states[-2].add_transition(new_data, states[-1]) 
    k = states[-2].suffix
    pi_1 = states[-2] # from shlomo's code
    # iteratively backtrack suffixes from state i - 1
    # adding shlomo's suggested improvement - gs 06.04.2012
    while k != 0:
        # trying this with < threshold
        dvec = [get_distance(new_data, s.data, weights) < threshold for s in k.transition]
        # if there is not a transition from the suffix
        if True not in dvec:
            k.add_transition(new_data, states[-1])
            pi_1 = k # from shlomo's code
            k = k.suffix
        else:
            break
    # if backtrack ended before state 0:
    if k == None or k == 0:
        states[-1].add_suffix(states[0])
    else:
        # filter out all above distance thresh - 06.04.2012
        filtered_transitions = filter(lambda x: get_distance(x.data, new_data, weights) <= threshold, k.transition)
        # sort the possible suffixes by lrs
        sorted_list = sorted(filtered_transitions, key = lambda x: x.pointer.lrs)
        for t in sorted_list:
            if get_distance(t.data, new_data, weights) <= threshold: 
                S_i = t
                states[-1].add_suffix(S_i.pointer)
                # add reverse suffix
                S_i.pointer.add_reverse_suffix(states[-1])
                break
    # LRS algorithm from shlomo's AOS.m
    ss = states[-1].suffix
    if ss == 0 or ss.number == 0 or ss.number == 1:
        states[-1].lrs = 0
    else:
        pi_2 = states[ss.number - 1]
        if pi_2 == pi_1.suffix:
            states[-1].lrs = pi_1.lrs + 1
        else:
            while pi_2.suffix != pi_1.suffix:
                pi_2 = pi_2.suffix
            states[-1].lrs = min(pi_1.lrs, pi_2.lrs) + 1

def build_oracle(input_data, threshold, feature = None):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    oracle = []

    # initialize weights 
    weights = {'mfcc': 0.0,            
               'centroid': 0.0,
               'rms': 0.0,
               'chroma': 0.0,
               'zerocrossings': 0.0}

    # weight the feature we want
    weights[feature] = 1.0

    add_initial_state(oracle)
    num_events = len(input_data)
    for i, event in enumerate(input_data):
        add_state(oracle, event, threshold, weights)
        # progress output
    return oracle 

def build_weighted_oracle(input_data, threshold, weights):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    oracle = []

    add_initial_state(oracle)
    num_events = len(input_data)
    for i, event in enumerate(input_data):
        add_state(oracle, event, threshold, weights)
        # progress output
    return oracle 
