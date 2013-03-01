############################################################
# IR.py 
# compute IR for a given PyOracle
# after Shlomo Dubnov
# modified 09.18.2012
# greg surges
# 2011 - 2012
# Shlomo modified 02.12.2013
###########################################################

import math
from scipy.signal import lfilter
import numpy as np

def encode(states):
    ''' 
    return code and compror for a given Oracle representation
    '''
    compror = []
    lrs = [x.lrs for x in states[1:]]
    sfx = []
    for x in states[1:]:
        if x.suffix == 0:
            sfx.append(0)
        else:
            sfx.append(x.suffix.number)

    # sfx = [x.suffix.number for x in states[1:]]
    code = [0] * len(states) # changed from code = []
    code[0] = (0,0) # changed from code = []
    
    j = 0 # changed from j = 1
    i = j
    cnt = 1 # changed from cnt = 2 (probably doesn't matter)
    while j < len(lrs):
        while i < len(lrs) - 1 and lrs[i + 1] >= i - j + 1:
            i = i + 1
        if i == j:
            i = i + 1
            code[cnt] = (0,i)
        else:
            #Shlomo: code.append((i - j, sfx[i] - i + j + 1))
            code[cnt] = (i - j, sfx[i] - i + j)
            compror.append((i,i-j)) #Shlomo: changed from compror.append(i) 
        cnt = cnt + 1
        j = i
    return code[0:cnt - 1], compror

def encode_old(states):
    ''' 
    return code and compror for a given Oracle representation
    '''
    compror = []
    lrs = [x.lrs for x in states[1:]]
    sfx = []
    for x in states[1:]:
        if x.suffix == 0:
            sfx.append(0)
        else:
            sfx.append(x.suffix.number)

    # sfx = [x.suffix.number for x in states[1:]]
    code = []
    code.append((0,1))
    
    j = 1
    i = j
    cnt = 1
    while j < len(lrs):
        while i < len(lrs) - 1 and lrs[i + 1] >= i - j + 1:
            i = i + 1
        if i == j:
            i = i + 1
            code.append((0,i))
        else:
            code.append((i - j, sfx[i] - i + j + 1))
            compror.append(i) 
        cnt = cnt + 1
        j = i
    return code, compror

def count_rev_suffixes(state):
    num = 1
    for s in state.reverse_suffix:
        num = num + count_rev_suffixes(s)
    return num


def ent(x):
    n = sum(x)
    h = 0
    for i in range(len(x)):
        p = float(x[i])/n
        h = h-p*math.log(p,2)
    return h

def extend_code(code):
    e_code = []
    for i in range(len(code)):
        e_code.append(code[i])
        if code[i][0] > 1:
            for j in range(code[i][0] - 1):
                e_code.append((-0.9999999, i))
    return e_code

def get_IR(states, alpha = 1.1):
    '''
    compress PyOracle and get IR
    new, time-evolving measure
    02.17.2013
    '''
    code, compror = encode(states)
    
    cw = [0] * len(code)
    for i, c in enumerate(code):
        cw[i] = c[0]+1

    c0 = [1 if x[0] == 0 else 0 for x in code]
    h0 = [math.log(x, 2) for x in np.cumsum(c0)]

    dti = [1 if x[0] == 0 else x[0] for x in code]
    ti = np.cumsum(dti)

    h = [0]*len(cw)

    for i in range(1, len(cw)):
        h[i] = ent(cw[0:i+1])

    h = np.array(h)
    h0 = np.array(h0)
    IR = ti, alpha*h0-h

    return IR, code, compror

    
def get_IR_old(states):
    '''
    compress PyOracle and get IR
    '''
    code, compror = encode_old(states)

    trn = [x.transition for x in states]
    sfx = []
    for x in states[1:]:
        if x.suffix == 0:
            sfx.append(0)
        else:
            sfx.append(x.suffix.number)
    lrs = [x.lrs for x in states]

    # proposed modification - 10.23.2012
    # takes into account that all transitions are not equally probably (occuring
    # with equal frequency over the length of the sequence
    P = [0] * len(states[0].transition)
    # rename
    N = []
    for t in states[0].transition: # for each new state
        N_i = count_rev_suffixes(t.pointer)
        N.append(N_i) 
    for i in range(len(P)):
        P[i] = float(N[i]) / sum(N)
    C0 = -1 * sum([p * math.log(p, 2) for p in P]) 

    # calculate IR from Compror
    IR = [0] * len(states)
    # C0 = math.log(len(trn[0]), 2)
    N = len(lrs)
    M = max(lrs)
    try:
        C1 = math.log(N, 2) + math.log(M, 2)
    except ValueError: # if log(0)
        C1 = math.log(N, 2) + math.log(0.0000000000000001, 2)
    for i in range(1, len(compror)):
        L = compror[i] - compror[i - 1]
        IR[compror[i - 1]:compror[i]] = [max(C0 - C1 / L, 0)] * L
    return IR, code, compror
