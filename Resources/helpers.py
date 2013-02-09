###################################################################################
# helpers.py
# simple helper functions for listen.py
# created 04.25.2012 greg surges
# modified 09.18.2012
# 2011 - 2012 greg surges
####################################################################################

import cPickle as pickle
import sys
import shelve
from scipy.signal import medfilt
import numpy as np
import midi
from matplotlib.mlab import find

from Resources.PyOracle.State import *
from Resources.PyOracle.Transition import *

from bregman.suite import *

features = ['mfcc', 'pitch', 'zerocross', 'brightness', 'centroid', 'rolloff', 'rms']

####################################################################################
# DATA MANGLERS
####################################################################################

def chunks(l, n):
    return [l[i:i+n] for i in xrange(0, len(l), n)]

def normalize(loaded_data):
    """ normalize dictionary of loaded events """
    max_zerocrossings = max([event['zerocrossings'] for event in loaded_data])  
    max_rms = max([event['rms'] for event in loaded_data]) 
    max_centroid = max([event['centroid'] for event in loaded_data]) 
    max_chroma = max(max([event['chroma'] for event in loaded_data]))
    max_mfcc = max(max([event['mfcc'] for event in loaded_data]))
    for event in loaded_data:
        event['rms'] = event['rms'] / (max_rms * 1.0)
        event['centroid'] = event['centroid'] / (max_centroid * 1.0)
        event['chroma'] = [x/max_chroma for x in event['chroma']]
        event['mfcc'] = [x/max_mfcc for x in event['mfcc']]
        event['zerocrossings'] = event['zerocrossings'] / (max_zerocrossings * 1.0) 
    return loaded_data

####################################################################################
# analysis / midi file helper functions
####################################################################################

fft_size = 8192
hop_size = 8192

def set_fft_size(n):
    global fft_size
    fft_size = n

def set_hop_size(n):
    global hop_size
    hop_size = n

def average_events(events, n):
    new_events = []
    # iterate by n over events
    for i in range(0, len(events), n):
        slice = events[i:i+n]
        tmp_event = {}
        tmp_event['time'] = events[i]['time']
        tmp_event['zerocrossings'] = float(sum([x['zerocrossings'] for x in slice])) / n 
        tmp_event['rms'] = float(sum([x['rms'] for x in slice])) / n
        tmp_event['centroid'] = float(sum([x['centroid'] for x in slice])) / n
        mfccs = [0] * 10
        for i, val in enumerate(mfccs):
            mfccs[i] = float(sum([x['mfcc'][i] for x in slice])) / n
        tmp_event['mfcc'] = mfccs
        chroma = [0] * 12
        for i,val in enumerate(chroma):
            chroma[i] = float(sum([x['chroma'][i] for x in slice])) / n
        tmp_event['chroma'] = chroma
        tmp_event['time'] = slice[0]['time']
        new_events.append(tmp_event)
    return new_events

def zerocrossings(filepath, size, h_size):
    ''' calculate and return zero crossings per size-block '''
    x, sr, fmt = wavread(filepath)    
    output_blocks = []
    # modified from https://gist.github.com/255291
    # for each block
    for n in range(0, len(x), h_size):
        current_samples = x[n:n+size]
        indices = find((current_samples[1:] >= 0) & (current_samples[:-1] < 0)) 
        # crossings = sum([1 for m in range(n, n+size) if x[m+1] > 0 and x[m] <= 0])
        output_blocks.append(len(indices))
    return output_blocks

def extract_audio_features(filepath):
    # first do mfccs
    features = {}
    mfcc = MelFrequencyCepstrum(filepath, ncoef=38, log10=True, nfft=fft_size,
            wfft=fft_size, nhop=hop_size)
    # get number of frames - each array in mfcc is one component
    frames = [[0]] * len(mfcc.X[0])
    num_frames = len(mfcc.X[0])
    for i, frame in enumerate(mfcc.X[0]):
        frames[i] = []
        for component in mfcc.X:
            frames[i].append(component[i])
    features['mfcc'] = frames
    rms = RMS(filepath, nfft=fft_size, wfft=fft_size, nhop=hop_size)
    features['rms'] = rms.X
    mf_spec_centroid = MelFrequencySpectrumCentroid(filepath, nfft=fft_size,
            wfft=fft_size, nhop=hop_size)
    features['centroid'] = mf_spec_centroid.X
    # chroma = Chromagram(filepath, log10=True, intensify=True, nfft=fft_size, wfft=fft_size, nhop=fft_size)
    chroma = HighQuefrencyChromagram(filepath, log10=True, intensify=True,
            nfft=fft_size, wfft=fft_size, nhop=hop_size)
    chroma_frames = [[0]] * len(chroma.X[0])
    for i, frame in enumerate(chroma.X[0]):
        chroma_frames[i] = []
        for component in chroma.X:
            chroma_frames[i].append(component[i])
    features['chroma'] = chroma_frames
    features['zerocrossings'] = zerocrossings(filepath, fft_size, hop_size)
    features['num_events'] = len(features['centroid'])
    return features

def features_to_events(features):
    events = []
    num_events = features['num_events']      
    mfcc = features['mfcc']
    rms = features['rms']
    centroid = features['centroid']
    chroma = features['chroma']
    zerocrossings = features['zerocrossings']
    event_time = 0.0
    for i in range(num_events):
        new_event = {}
        new_event['time'] = event_time / 44.100
        new_event['mfcc'] = mfcc[i]
        new_event['rms'] = rms[i]
        new_event['centroid'] = centroid[i]
        new_event['chroma'] = chroma[i]
        new_event['zerocrossings'] = zerocrossings[i]
        new_event['time'] = fft_size * i
        events.append(new_event) 
        event_time += fft_size
    return events

####################################################################################
# oracle file helpers 
####################################################################################

def process_oracle_for_shelve(oracle):
    processed_oracle = []
    for state in oracle:
        new_state = {}
        try:
            new_state['number'] = state.number
        except:
            print 'failed on number'
        try:
            new_state['lrs'] = state.lrs
        except:
            print 'failed lrs'
        try:
            if state.suffix:
                new_state['suffix'] = state.suffix.number
            else:
                new_state['suffix'] = state.suffix
        except:
            print state.suffix
            print 'failed suffix'
        try:
            new_state['reverse_suffix'] = [r.number for r in state.reverse_suffix]
        except:
            print 'failed rev suf'
        try:
            new_state['transition'] = [t.pointer.number for t in state.transition]
        except:
            print 'failed transition'
        processed_oracle.append(new_state)
    return processed_oracle

def process_shelve_to_oracle(shelved_oracle):
    oracle = [State(n) for n in range(len(shelved_oracle))]
    for i, state in enumerate(shelved_oracle):
        oracle[i] = State(state['number'])
        oracle[i].add_suffix(oracle[state['suffix']])
        oracle[i].transition = [Transition(oracle[t], oracle[t]) for t in state['transition']]
        oracle[i].lrs = state['lrs']
        oracle[i].reverse_suffix = [oracle[rs] for rs in state['reverse_suffix']]
    return oracle

def save_oracle(oracle, filename):
    sys.setrecursionlimit(50000)
    file = shelve.open(filename)
    processed_oracle = process_oracle_for_shelve(oracle)
    file['oracle'] = processed_oracle
    file.close()

def load_oracle(filename):
    oracle = []
    file = shelve.open(filename)
    local_oracle = file['oracle']
    local_oracle = process_shelve_to_oracle(local_oracle)
    oracle = local_oracle
    file.close()
    return oracle

####################################################################################
# IR filtering
####################################################################################

def apply_median(data, k_size):
    keys = sorted(data.keys())
    array = [data[key] for key in keys]
    array = np.array(array) 
    array = medfilt(array, k_size)
    array = {key: val for (key, val) in zip(keys, array)}
    return array
