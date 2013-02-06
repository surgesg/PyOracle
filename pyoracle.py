'''
pyoracle.py

01.15.2013
greg surges

audio oracle analysis in python
'''

import Resources.helpers
import Resources.PyOracle.PyOracle
import Resources.PyOracle.IR
import Resources.DrawOracle

def make_features(filename, fft_size = 4096):
    '''
    extract list of features from audio file, using Bregman module
    features = ['mfcc', 'centroid', 'rms', 'chroma', 'zerocrossings']
    '''
    Resources.helpers.set_fft_size(fft_size)
    features = Resources.helpers.extract_audio_features(filename)
    return features

def make_oracle(threshold, features_list, feature, frames_per_state = 1):
    '''
    build an oracle given:
        threshold - distance function theshold
        features_list - feature vector (from pyoracle.make_features)
        feature - string indicating which feature the oracle should be built on
        frames_per_state - average n analysis frames to make one oracle state
    '''
    events = Resources.helpers.features_to_events(features_list)
    events = Resources.helpers.average_events(events, frames_per_state)
    oracle = Resources.PyOracle.PyOracle.build_oracle(events, threshold, feature)
    return oracle

def make_weighted_oracle(threshold, features_list, weights):
    '''
    build an oracle given:
        threshold - distance function theshold
        features_list - feature vector (from pyoracle.make_features)
        weights - dict() with a weight for each feature in features_list, used
            in computing distance function
    '''
    events = Resources.helpers.features_to_events(features_list)
    oracle = Resources.PyOracle.PyOracle.build_weighted_oracle(events, threshold, weights)
    return oracle

def make_dynamic_oracle(threshold, features_list, weights):
    '''
    build an oracle given:
        threshold - distance function theshold
        features_list - feature vector (from pyoracle.make_features)
        weights - dict() with a weight for each feature in features_list, used
            in computing distance function
    '''
    events = Resources.helpers.features_to_events(features_list)
    oracle = Resources.PyOracle.PyOracle.build_dynamic_oracle(events, threshold, weights)
    return oracle

def calculate_ir(oracle):
    '''
    calculate information rate (IR) for a given oracle
    '''
    IR, code, compror = Resources.PyOracle.IR.get_IR(oracle)
    return IR, code, compror

def save_oracle(oracle, filename):
    print 'saving to ', filename
    Resources.helpers.save_oracle(oracle, filename)
    print 'done!'

def load_oracle(filename):
    print 'loading "', filename, '"'
    oracle = Resources.helpers.load_oracle(filename)
    print 'done!'
    return oracle

def draw_oracle(oracle, filename):
    image = Resources.DrawOracle.start_draw(oracle) 
    image.save(filename)
    pass 


