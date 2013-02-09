'''
generate.py
'''

import random
import numpy as np
from matplotlib.mlab import find

def generate(oracle, seq_len, p, k):
    '''
    generate output state vector from audio oracle
    inputs:
    oracle - audio oracle to use
    seq_len - length of output sequence in states
    p - probability of jump
    k - starting state
    outputs:
    s - new_sequence
    kend - end point
    ktrace
    '''

    s = []
    ktrace = [1]

    for i in range(seq_len):
        # generate each state
        if oracle[k].suffix != 0:
            if (random.random() < p):
                #copy forward according to transitions
                I = oracle[k].transition
                I = [t.pointer.number for t in I]
                sym = I[int(np.floor(random.random()*len(I)))]
                s.append(sym-1)
                k = sym
                ktrace.append(k)
                pass
            else:
                # copy any of the next symbols
                k = oracle[k].suffix.number
                ktrace.append(k)
                I = oracle[k].transition
                I = [t.pointer.number for t in I]
                sym = I[int(np.floor(random.random()*len(I)))]
                s.append(sym-1)
                k = sym
                ktrace.append(k)
        else:
            if k < len(oracele):
                next_k = find([o.transition.pointer.number for o in oracle] == k+1)
                s.append(next_k)
                k = k+1
                ktrace.append(k)
            else:
                nextk = random.random*len(oracle)
                s.append(find([p.pointer.number for p in oracle[0].transtion] == nextk))
                k = nextk
                ktrace.append(k)
    kend = k
    return s, kend, ktrace

