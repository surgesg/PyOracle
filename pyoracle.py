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
    features = Resources.helpers.extract_audio_features(filename)
    return features

def make_oracle(threshold, features_list, feature):
    events = Resources.helpers.features_to_events(features_list)
    oracle = Resources.PyOracle.PyOracle.build_oracle(events, threshold, feature)
    return oracle

def calculate_ir(oracle):
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
