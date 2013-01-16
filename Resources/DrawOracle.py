from Tkinter import * 
import PyOracle.State
from random import randint

width = 645.0
height = 400.0
oracle = []
canvas = []

lrs_threshold = 0

def start_draw(frame, _oracle, features, feature, current_state):
    global oracle
    global canvas
    canvas = Canvas(frame, background = '#000000', width=645, height=400)
    canvas.grid(row=5, column=1, rowspan=9)
    for i, f in enumerate(features):
        if feature == f: 
            oracle = _oracle[i] 
            return draw(current_state)

def draw(current_state):
    canvas.create_rectangle(0,0, 646.0, 401.0, fill='black')
    for i, state in enumerate(oracle):
        # draw circle for each state
        x_pos = (float(i) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
        # iterate over forward transitions
        for tran in state.transition:
            # if forward transition to next state
            if tran.pointer.number == i + 1:
                # draw forward transitions
                next_x = (float(i + 1) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
                current_x = x_pos + (0.25 / len(oracle) * width)
                canvas.create_line(current_x, height / 2, next_x, height / 2,
                        fill='white')
            else:
                if tran.pointer.lrs >= lrs_threshold:
                    # forward transition to another state
                    current_x = x_pos
                    next_x = (float(tran.pointer.number) / len(oracle) * width) + (0.5 / len(oracle) * width)
                    arc_height = (height / 2) + (tran.pointer.number - state.number) * 0.125
                    canvas.create_arc(current_x, 
                                      (height / 2) + (arc_height / 2),
                                      next_x,
                                      height / 2 - (arc_height / 2),
                                      style=ARC,
                                      outline='#ffffff',
                                      start = -180, extent = -180)
        if state.suffix:
            if state.suffix.number != 0 and state.suffix.lrs >= lrs_threshold:
                current_x = x_pos
                next_x = (float(state.suffix.number) / len(oracle) * width) + (0.5 / len(oracle) * width)
                # draw arc
                arc_height = (height / 2) - (state.suffix.number - state.number) * 0.125
                canvas.create_arc(current_x,
                                  (height / 2) + (arc_height / 2),
                                  next_x,
                                  height / 2 - (arc_height / 2),
                                  style=ARC,
                                  outline='white',
                                  start = -180, extent = 180)
        '''
        for r_suffix in state.reverse_suffix:
            if r_suffix.number != 0 and r_suffix.lrs >= lrs_threshold:
                current_x = x_pos
                next_x = (float(r_suffix.number) / len(oracle) * width) + (0.5 / len(oracle) * width)
                # draw arc
                arc_height = (height / 2) - (r_suffix.number - state.number) * 0.125
                canvas.create_arc(current_x,
                                  (height / 2) + (arc_height / 2),
                                  next_x,
                                  height / 2 - (arc_height / 2),
                                  style=ARC,
                                  outline='white',
                                  start = -180, extent = 180)
        '''
    # draw circles on top
    for i, state in enumerate(oracle):
        color = 'white'
        if i == current_state:
            color = 'red'
        x_pos = (float(i) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
        circle_width = (0.5 / len(oracle) * width) / 2 
        canvas.create_arc(x_pos - circle_width, 
                          (height / 2) - circle_width,
                          x_pos + circle_width,
                          (height / 2) + circle_width,
                          style=PIESLICE,
                          fill = color,
                          outline = color, start = 0, extent = -359)
    return canvas
    # save_image(filename)
