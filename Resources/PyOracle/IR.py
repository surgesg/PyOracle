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
            #Shlomo: code.append((i - j, sfx[i] - i + j + 1))
            code.append((i - j, sfx[i] - i + j))
            compror.append((i,i-j)) #Shlomo: changed from compror.append(i) 
        cnt = cnt + 1
        j = i
    return code, compror

def count_rev_suffixes(state):
    num = 1
    for s in state.reverse_suffix:
        num = num + count_rev_suffixes(s)
    return num

def get_IR(states):
    '''
    compress PyOracle and get IR
    '''
    code, compror = encode(states)

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
    alpha = 1 #variable to test the sensitivity to CO scaling
    
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
        #print i
        #Shlomo:        L = compror[i] - compror[i - 1] 
        L = compror[i][1]
        #print len(IR), L, compror[i] - L, compror[i]
        #Shlomo:       IR[compror[i - 1] + 1:compror[i]] = [C0 - C1 / j for j in range(1, L)]
        IR[compror[i][0] - L :compror[i][0]] = [C0*alpha - C1 / j for j in range(1, L)]
 
    IR = [max(0, x) for x in IR]
    return IR, code, compror
    
    '''		
    print 'done'
    
    mem_len = 20
    B_coefs = [1.0 / mem_len for i in range(0, mem_len)]
    IR = lfilter(B_coefs, [1], IR)
    '''

def get_IR_old(states):
    '''
    compress PyOracle and get IR
    '''
    code, compror = encode(states)

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
