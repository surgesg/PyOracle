#############################################################################
# pyoracle.py 
# builds a factor oracle from an input string of audio features
# modified 03.18.2013
# greg surges
# copyleft 2011 - 2013
#############################################################################

import time

import State
from random import randint
from itertools import izip

oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}
features = ['mfcc', 'centroid', 'rms', 'chroma', 'zerocrossings']
#############################################################################
# ORACLE CONSTRUCTION FUNCTIONS
#############################################################################

def get_distance(event1, event2, weights = None):
    '''
    get distance between frames
    '''
    features = event1.keys()
    if 'time' in features:
        features.remove('time')

    distance = 0

    # if no weight, initialize by weighting all features equally
    if weights == None:
        weights = {}
        for feature in features:
            weights[feature] = 1.0

    for feature in features:
        # get length of feature vec 
        try:
            n = len(event1[feature])
        except:
            n = 1
        if n > 1:
            # is a vector
            data = izip(event1[feature], event2[feature])
            data = sum((a - b) * (a - b) for a, b in data) / n
            data *= weights[feature]
            distance += data
        else:
            # is a scaler
            data = ((event1[feature] - event2[feature]) * (event1[feature] - event2[feature]))
            data *= weights[feature]
            distance += data
    return distance

'''
def add_initial_state(states):
    states.append(State.State(0))
'''
def add_initial_state(oracle):
    oracle['sfx'].append(None)
    oracle['rsfx'].append([])
    oracle['trn'].append([])
    oracle['lrs'].append(0)
    oracle['data'].append(0)

def add_state(oracle, new_data, threshold = 0, weights = None):
    # create new state
    oracle['sfx'].append(0)
    oracle['rsfx'].append([])
    oracle['trn'].append([])
    oracle['lrs'].append(0)
    oracle['data'].append(new_data)
    n_states = len(oracle['lrs']) 
    i = n_states - 1

    # assign new transition from state i-1 to i
    oracle['trn'][i - 1].append(i)

    k = oracle['sfx'][i - 1] 
    print n_states, i, k
    pi_1 = i - 1

    # iteratively backtrack suffixes from state i-1
    while k != None:
        dvec = [get_distance(new_data, oracle['data'][s], weights) < threshold for s in oracle['trn'][k]]
        # if no transition from suffix
        if True not in dvec:
            oracle['trn'][k].append(i)
            pi_1 = k
            k = oracle['sfx'][k]
        else:
            break
    # if backtrack ended before 0
    if k == None:
        oracle['sfx'][i] = 0
    else:
        # filter out all above distance thresh
        filtered_transitions = filter(lambda x: get_distance(oracle['data'][x], new_data, weights) <= threshold, oracle['trn'][k])
        # sort possible suffixes by LRS
        sorted_list = sorted(filtered_transitions, key = lambda x: oracle['lrs'][x])
        for t in sorted_list:
            if get_distance(oracle['data'][t], new_data, weights) <= threshold:
                # add suffix
                S_i = t
                oracle['sfx'][i] = S_i
                
                # add rev suffix
                oracle['rsfx'][S_i] = i
                break
    # LRS 
    ss = oracle['sfx'][-1]
    if ss == 0 or ss == 1:
        oracle['lrs'][-1] = 0
    else:
        pi_2 = ss - 1
        if pi_2 == oracle['sfx'][pi_1]:
            oracle['lrs'][-1] = oracle['lrs'][pi_1] + 1
        else:
            while oracle['sfx'][pi_2] != oracle['sfx'][pi_1]:
                pi_2 = oracle['sfx'][pi_2]
            oracle['lrs'][-1] = min(oracle['lrs'][pi_1], oracle['lrs'][pi_2]) + 1

'''
def add_state(states, new_data, threshold = 0, weights = None):
    # create a new state numbered i
    new_state = State.State(len(states))
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
'''

def build_oracle(input_data, threshold, feature = None):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    global oracle

    oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}
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

def build_dynamic_oracle(input_data, threshold, weights):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    oracle = []

    add_initial_state(oracle)
    num_events = len(input_data)
    for i, event in enumerate(input_data):
        add_state(oracle, event, threshold, weights[i])
        # progress output
    return oracle 
