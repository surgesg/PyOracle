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

def make_features(filename):
    '''
    extract list of features from audio file, using Bregman module
    features = ['mfcc', 'centroid', 'rms', 'chroma', 'zerocrossings']
    '''
    features = Resources.helpers.extract_audio_features(filename)
    return features

def make_oracle(threshold, features_list, feature):
    '''
    build an oracle given:
        threshold - distance function theshold
        features_list - feature vector (from pyoracle.make_features)
        feature - string indicating which feature the oracle should be built on
    '''
    events = Resources.helpers.features_to_events(features_list)
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
