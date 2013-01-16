#############################################################################
# pyforacle.py 
# builds a factor oracle from an input string of midi events
# modified 09.18.2012
# greg surges
# copyleft 2011 - 2012
#############################################################################

import State
from random import randint

oracle = []

#############################################################################
# ORACLE CONSTRUCTION FUNCTIONS
#############################################################################

def add_initial_state(states):
    states.append(State.State(0))

def add_state(states, new_data, distance_function = None, threshold = 0):
    # create a new state numbered i
    new_state = State.State(len(states))
    states.append(new_state) 
    # assign a new transition from state i - 1 to state i
    states[-2].add_transition(new_data, states[-1]) 
    k = states[-2].suffix
    pi_1 = states[-2]
    # iteratively backtrack suffixes from state i - 1
    while k and (new_data not in [s.data for s in k.transition]):
        k.add_transition(new_data, states[-1])
        pi_1 = k # from shlomo's code
        k = k.suffix
    # if backtrack ended before state 0:
    if k:
        for t in k.transition:
            if t.data == new_data:
                S_i = t
        states[-1].add_suffix(S_i.pointer)
    else:
        states[-1].add_suffix(states[0])
    # LRS algorithm from S.D.
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

def build_oracle(input_data, feature = None):
    '''
    need this function to hvae the same signature as the PyOracle version,
    but will ignore the threshold and feature (for now)
    '''
    oracle = []
    add_initial_state(oracle)
    num_events = len(input_data)
    for i, event in enumerate(input_data):
        add_state(oracle, event[feature])
    return oracle    

def main():
    global oracle
    oracle = []
    add_initial_state(oracle) 
    word = raw_input('enter string: ') 
    for c in word:
        add_state(oracle, c)
    for i, state in enumerate(oracle):
        state.pretty_print()

if __name__ == '__main__':
    main()
