'''
pyoracle.py

01.15.2013
greg surges

audio oracle analysis in python
'''
import Resources.helpers
import Resources.PyOracle.PyOracle
import Resources.PyOracle.IR

def make_oracle(filename, threshold, feature):
    features = Resources.helpers.extract_audio_features(filename) 
    events = Resources.helpers.features_to_events(features)
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
