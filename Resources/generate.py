'''
generate.py
'''

import random
import numpy as np
from matplotlib.mlab import find
from scipy.io import wavfile

import PyOracle.IR

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
                if len(I) == 0:
                    # if last state, choose a suffix
                    k = oracle[k].suffix.number
                    ktrace.append(k)
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

def make_win(n):
    win = np.array([np.hanning(n) + 0.00001, np.hanning(n) + 0.00001])
    win = np.transpose(win)
    return win

def generate_audio(ifilename, ofilename, buffer_size, hop, oracle, seq_len, p, k):
    fs, x = wavfile.read(ifilename)
    xmat = []
    for i in range(0, len(x), hop):
        new_mat = np.array(x[i:i+buffer_size]) # try changing array type?
        xmat.append(new_mat)
    xmat = np.array(xmat)

    s, kend, ktrace = generate(oracle, seq_len, p, k) 
    xnewmat = xmat[:, s]

    framelen = len(xnewmat[0])
    nframes = len(xnewmat)

    wsum = np.zeros(((nframes-1) * hop + framelen, 2)) 

    win = make_win(framelen)

    x = np.zeros(((nframes-1) * hop + framelen, 2)) 
    win_pos = range(0, len(x), hop)
    for i in range(0, nframes):
        # this is the overlap add sec
        win = make_win(len(xnewmat[i]))
        x[win_pos[i]:win_pos[i]+len(xnewmat[i])] = x[win_pos[i]:win_pos[i]+len(xnewmat[i])] + xnewmat[i] * win
        wsum[win_pos[i]:win_pos[i]+len(xnewmat[i])] = wsum[win_pos[i]:win_pos[i]+len(xnewmat[i])] + win 
    x[hop:-hop] = x[hop:-hop] / wsum[hop:-hop]
    x = np.array(x, dtype=np.int)


    wavfile.write(ofilename, fs, x)
    return x, wsum

def generate_on_ir(ifilename, ofilename, buffer_size, hop, oracle, seq_len, p, k):
    '''
    generate to maximize IR over sequence
    inputs:
        oracle      - input oracle
        seq_len     - output sequence length
        k           - initial state
    '''
    fs, x = wavfile.read(ifilename)
    xmat = []
    for i in range(0, len(x), hop):
        new_mat = np.array(x[i:i+buffer_size]) # try changing array type?
        xmat.append(new_mat)
    xmat = np.array(xmat)
    
    ir = PyOracle.IR.get_IR(oracle)[0]
                                                                                                               
    k = sorted(range(0, len(oracle)), key=lambda x: ir[x])[-1]
    print k

    s,kend,ktrace = compare_path(oracle, seq_len, ir, k) 
    xnewmat = xmat[:, s]
                                                                                                               
    framelen = len(xnewmat[0])
    nframes = len(xnewmat)
                                                                                                               
    wsum = np.zeros(((nframes-1) * hop + framelen, 2)) 
                                                                                                               
    win = make_win(framelen)
                                                                                                               
    x = np.zeros(((nframes-1) * hop + framelen, 2)) 
    win_pos = range(0, len(x), hop)
    for i in range(0, nframes):
        # this is the overlap add sec
        win = make_win(len(xnewmat[i]))
        x[win_pos[i]:win_pos[i]+len(xnewmat[i])] = x[win_pos[i]:win_pos[i]+len(xnewmat[i])] + xnewmat[i] * win
        wsum[win_pos[i]:win_pos[i]+len(xnewmat[i])] = wsum[win_pos[i]:win_pos[i]+len(xnewmat[i])] + win 
    x[hop:-hop] = x[hop:-hop] / wsum[hop:-hop]
    x = np.array(x, dtype=np.int)
                                                                                                               
    wavfile.write(ofilename, fs, x)
    return x, wsum

def compare_path(oracle, seq_len, ir_vec, k):
    s = []
    ktrace = [1]

    for i in range(seq_len):
        # generate each state
        if k+1 < len(ir_vec) and ir_vec[k+1] > ir_vec[k]:
            k = k + 1
            ktrace.append(k)
            s.append(k)
        else:
            pos = [t.pointer.number for t in oracle[k].transition]
            try:
                pos.append(oracle[k].suffix.number)
            except:
                pos.append(oracle[k].suffix)
            for item in ktrace:
                if item in pos:
                    pos.remove(item)
            pos = sorted(pos, key=lambda x: ir_vec[x], reverse = True)
            k = pos[0]
            ktrace.append(k)
            s.append(k)
    kend = k
    return s, kend, ktrace
