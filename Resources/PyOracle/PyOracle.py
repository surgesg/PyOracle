#############################################################################
# pyoracle.py 
# builds a factor oracle from an input string of audio features
# modified 03.18.2013
# greg surges
# copyleft 2011 - 2013
#############################################################################

import time

from random import randint
from itertools import izip
from numpy import array, size, zeros, shape, log, exp
from math import isnan

oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}
#############################################################################
# ORACLE CONSTRUCTION FUNCTIONS
#############################################################################

def get_distance(event1, event2, weights = None, dfunc = 'euclidian'):
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
        if dfunc == 'euclidian':
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
        elif dfunc == 'bregman':
            # multinomial bregman
            sevent1 = event1[feature]
            sevent2 = event2[feature]
            data = multinomial_bregman_div(sevent1, sevent2) 
            if isnan(data):
                data = 1000
                print feature, event1[feature]
            distance += data * weights[feature]
        # print feature, distance
    return distance

def add_initial_state(oracle):
    oracle['sfx'].append(None)
    oracle['rsfx'].append([])
    oracle['trn'].append([])
    oracle['lrs'].append(0)
    oracle['data'].append(0)

def add_state(oracle, new_data, threshold = 0, weights = None, dfunc = 'euclidian'):
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
    pi_1 = i - 1

    # iteratively backtrack suffixes from state i-1
    while k != None:
        dvec = [get_distance(new_data, oracle['data'][s], weights, dfunc) < threshold for s in oracle['trn'][k]]
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
        filtered_transitions = filter(lambda x: get_distance(oracle['data'][x], new_data, weights, dfunc) <= threshold, oracle['trn'][k])
        # sort possible suffixes by LRS
        sorted_list = sorted(filtered_transitions, key = lambda x: oracle['lrs'][x])
        for t in sorted_list:
            if get_distance(oracle['data'][t], new_data, weights, dfunc) <= threshold:
                # add suffix
                S_i = t
                oracle['sfx'][i] = S_i
                
                # add rev suffix
                if type(oracle['rsfx'][S_i]) == list:
                    oracle['rsfx'][S_i].append(i)
                else:
                    oracle['rsfx'][S_i] = [i]
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

def build_oracle(input_data, threshold, feature = None, weights = None, dfunc = 'euclidian'):
    global oracle

    oracle = {'sfx': [], 'trn': [], 'rsfx': [], 'lrs': [], 'data': []}

    # initialize weights if needed 
    if weights == None:
        weights = {'mfcc': 0.0,            
                   'centroid': 0.0,
                   'rms': 0.0,
                   'chroma': 0.0,
                   'zerocrossings': 0.0}

        # weight the feature we want
        weights[feature] = 1.0

    add_initial_state(oracle)
    for event in input_data:
        add_state(oracle, event, threshold, weights, dfunc)
    return oracle 

def build_weighted_oracle(input_data, threshold, weights):
    oracle = []

    add_initial_state(oracle)

    for event in input_data:
        add_state(oracle, event, threshold, weights)
    return oracle 

def build_dynamic_oracle(input_data, threshold, weights):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    oracle = []

    add_initial_state(oracle)
    for i, event in enumerate(input_data):
        add_state(oracle, event, threshold, weights[i])
        # progress output
    return oracle 

def vector_to_distribution(q):
    d = q
    # print d, d.shape
    try:
        for i, data in enumerate(q):
            d[i,:] = d[i,:] / sum(d[i,:])
    except TypeError:
        pass
    except IndexError:
        pass
    return d

def dist_to_multinomial(q):
    '''
    convert raw distributions to multinomial natural parameters
    see : http://cosmal.ucsd.edu/~arshia/musant/?n=InformationGeometry.ExponentialFamilies
    '''
    
    q = array(q)
    shape_q = shape(q)
    # print 'shape q:', shape(q), 'q:', q
    if shape(q) == ():
        d = 1
        n = 1
    else:
        d = len(q) # dimensions
        n = 1
        
    if d > 1:
    # normalize Qs to make sre they are distributions
        q = vector_to_distribution(q)
    # print 'normalized Qs:', q 
    theta = zeros((d))
    # print theta, n, d
    
    try:
        for i in range(0, d):
            # print q[i] / q[d-1]
            # is this abs() misplaced?
            theta[i] = log(abs(q[i] / q[d-1]) + 0.0000001)
    except IndexError:
        # single number
        # print 'q after indexerror:', q
        theta = log(abs(q))
    
    # print 'theta: ', theta
    return theta

def multinomial_grad_f(theta):
    # f is the cumulant function of the multinomial exponential canonical form
    s = 0.0
    
    try:
        s = sum(exp(theta))
    except TypeError:
        s = exp(theta)
    result = exp(theta) / (1+s)
    
    return result

def F(p):
    # print p
    try:
        return log(1 + sum(exp(p)))
    except TypeError:
        return log(1+exp(p))

def multinomial_bregman_div(p, q):
    p = dist_to_multinomial(p)
    q = dist_to_multinomial(q)
    pq = p - q
    try:
        result = F(p) - F(q) - sum(pq * multinomial_grad_f(q))
    except TypeError:
        result = F(p) - F(q) - (pq * multinomial_grad_f(q))
    return result
