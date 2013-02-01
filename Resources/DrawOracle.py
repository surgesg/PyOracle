import PyOracle.State
from random import randint

from PIL import Image, ImageDraw, ImageFilter

width = 900 * 4 
height = 400 * 4
oracle = []
image = []

lrs_threshold = 0

def start_draw(_oracle):
    global oracle
    global image
    current_state = 0
    image = Image.new('RGB', (width, height))
    oracle = _oracle 
    return draw(current_state)

def draw(current_state):
    # handle to Draw object - PIL
    draw = ImageDraw.Draw(image)
    for i, state in enumerate(oracle):
        # draw circle for each state
        x_pos = (float(i) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
        # iterate over forward transitions
        for tran in state.transition:
            # if forward transition to next state
            print i, tran.pointer.number
            if tran.pointer.number == i + 1:
                # draw forward transitions
                print 'line'
                next_x = (float(i + 1) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
                current_x = x_pos + (0.25 / len(oracle) * width)
                draw.line((current_x, height/2, next_x, height/2), width=1,fill='white')
            else:
                if tran.pointer.lrs >= lrs_threshold:
                    # forward transition to another state
                    current_x = x_pos
                    next_x = (float(tran.pointer.number) / len(oracle) * width) + (0.5 / len(oracle) * width)
                    arc_height = (height / 2) + (tran.pointer.number - state.number) * 0.125
                    draw.arc((int(current_x), int(height/2 - arc_height/2),
                        int(next_x), int(height/2 + arc_height / 2)), 180, 0,
                        fill='White')
        if state.suffix:
            if state.suffix.number != 0 and state.suffix.lrs >= lrs_threshold:
                current_x = x_pos
                next_x = (float(state.suffix.number) / len(oracle) * width) + (0.5 / len(oracle) * width)
                # draw arc
                arc_height = (height / 2) - (state.suffix.number - state.number) * 0.125
                draw.arc((int(next_x), 
                          int(height/2 - arc_height/2), 
                          int(current_x), 
                          int(height/2 + arc_height/2)),
                        0,
                        180,
                        fill='White')
    # draw circles on top
    for i, state in enumerate(oracle):
        color = 'white'
        if i == current_state:
            color = 'red'
        x_pos = (float(i) / len(oracle) * width) + 0.5 * 1.0 / len(oracle) * width
        circle_width = (0.5 / len(oracle) * width) / 2 
        draw.ellipse([x_pos - circle_width, height/2 - circle_width,
            x_pos+circle_width, height/2 + circle_width], outline='white', fill='white')
    image.resize((900, 400), (Image.BILINEAR))
    return image
