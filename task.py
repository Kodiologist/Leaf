#!/usr/bin/env python
# encoding: UTF-8

from sys import argv
from time import sleep
from psychopy.event import getKeys, clearEvents
from psychopy.visual import Rect, Line, TextStim, Circle
import schizoidpy

par = dict(zip(argv[1::2], argv[2::2])) # DEPLOYMENT SCRIPT EDITS THIS LINE

o = schizoidpy.Task(
    button_radius = .12,
    okay_button_pos = (0, -.7))
o.save('task', par['task'])

opponent_cooperates = [
    0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1,
    0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1]
  # A shuffle of twenty 0s and 1s.

# ------------------------------------------------------------
# * Declarations
# ------------------------------------------------------------

def Boolish(class_name, v1_name, v2_name):
    'Create a Boolean-like class.'
    cls = type(class_name, (object,), dict())
    v1 = cls()
    v2 = cls()
    cls.from_bool = classmethod(lambda self, x: v2 if x else v1)
    cls.__nonzero__ = lambda self: self is v2
    cls.__repr__ = lambda self: v2_name if self is v2 else v1_name
    v1.flip = v2
    v1.sign = -1
    v2.flip = v1
    v2.sign = 1
    globals()[class_name] = cls
    globals()[v1_name] = v1
    globals()[v2_name] = v2

Boolish('Choice', 'DEFECT', 'COOPERATE')
Boolish('HDir', 'LEFT', 'RIGHT')
Boolish('VDir', 'DOWN', 'UP')

opponent_choices = map(Choice.from_bool, opponent_cooperates)

choice_colors = {COOPERATE: 'green', DEFECT: 'blue'}
choices_by_side = {
    LEFT: COOPERATE, RIGHT: DEFECT,
    UP: COOPERATE, DOWN: DEFECT}
payoffs = {
  # The first element of each pair is the player whose payoffs
  # we're asking about.
   (DEFECT, COOPERATE): 4,
   (COOPERATE, COOPERATE): 3,
   (DEFECT, DEFECT): 2,
   (COOPERATE, DEFECT): 1}

# Opponent choice boxes
def f():
    hmargin = .05
    vmargin = .7
    hspacer = .03
    vspacer = .03
    row_len = 4
    width = .05  # (2 - 2*margin - (row_len - 1) * hspacer)/row_len
    height = .05
    pos = lambda i: (
        +width/2 + -1 + hmargin + (i % row_len)*(width + hspacer),
        -height/2 + 1 - vmargin - int(i / row_len)*(height + vspacer))
    boxes = [
        Rect(o.win,
            fillColor = choice_colors[c], lineColor = 'black',
            width = width, height = height,
            pos = pos(i))
        for i, c in enumerate(opponent_choices)]
    marker_f = lambda i: Circle(o.win,
        lineColor = 'black', fillColor = 'yellow',
        radius = min(width, height)/4,
        pos = pos(i))
    return boxes, marker_f
opponent_choice_boxes, opponent_choice_marker = f()

# Payoff matrix
def f():
    x_offset = .3
    y_offset = -.2
    length = 1.
    linewidth = 3
       # lineWidth arguments are in pixels.
    cwidth = length/5
    cheight = cwidth/2
    def gridsquare(hside, vside):
        x = hside.sign * length/4 + x_offset
        y = vside.sign * length/4 + y_offset
        player_points = payoffs[
            choices_by_side[hside],
            choices_by_side[vside]]
        opponent_points = payoffs[
            choices_by_side[vside],
            choices_by_side[hside]]
        gridline = lambda x1, y1, x2, y2: Line(o.win,
            lineColor = 'black', lineWidth = linewidth,
            start = (x + x1 * length/4, y + y1 * length/4),
            end = (x + x2 * length/4, y + y2 * length/4))
        return [
            gridline(-1, -1,  -1,  1),
            gridline(-1,  1,   1,  1),
            gridline( 1,  1,   1,  -1),
            gridline( 1, -1,  -1,  -1),
            gridline(-1,  1,   1,  -1),
            TextStim(o.win, str(opponent_points), color = 'black',
                pos = (x - length/8, y - length/8),
                height = .1),
            TextStim(o.win, str(player_points), color = 'black',
                pos = (x + length/8, y + length/8),
                height = .2)]
    card = lambda side, x, y: Rect(o.win,
        fillColor = choice_colors[choices_by_side[side]],
        lineColor = 'black',
        width = cwidth, height = cheight, pos = (x + x_offset, y + y_offset))
    stims = (
        gridsquare(LEFT, UP) + 
        gridsquare(RIGHT, UP) +
        gridsquare(RIGHT, DOWN) +
        gridsquare(LEFT, DOWN) + [
        card(LEFT, -length/4, length/2 + cheight/2 + .05),
        card(RIGHT, length/4, length/2 + cheight/2 + .05),
        o.text(x_offset, length/2 + y_offset + .3, 'You play'),
        card(UP, -length/2 - cwidth/2 - .05, length/4),
        card(DOWN, -length/2 - cwidth/2 - .05, -length/4),
        o.text(x_offset - length/2 - .2, -.2, 'They\nplay')])
    marker_f = lambda hside, vside: Rect(o.win,
        fillColor = 'yellow', lineColor = None, opacity = .3,
        width = length/2, height = length/2,
        pos =
           (hside.sign * length/4 + x_offset,
            vside.sign * length/4 + y_offset))
    grayout_f = lambda vside: Rect(o.win,
        fillColor = 'white', lineColor = None, opacity = .7,
        width = length, height = length/2,
        pos = (x_offset, vside.sign * length/4 + y_offset))
    return stims, marker_f, grayout_f
pmatrix, pmatrix_marker, pmatrix_shade = f()

def do_trial(trial):
    dkey = ('cooperated', trial)
    opponent_side = UP if choices_by_side[UP] is opponent_choices[trial] else DOWN
    stims = (opponent_choice_boxes + pmatrix + [
         pmatrix_shade(opponent_side.flip),
         opponent_choice_marker(trial)])
    o.draw(*stims)
    with o.timestamps(dkey):
        while True:
            pressed = getKeys(['escape', 'left', 'right'])
            if 'escape' in pressed:
                quit()
            if len(pressed) == 1:
                break
            clearEvents()
            sleep(.1)
    chosen_side = LEFT if pressed[0] == 'left' else RIGHT
    o.save(dkey,
        choices_by_side[chosen_side] is COOPERATE)
    o.wait_screen(.5, *(stims + [
        pmatrix_marker(chosen_side, opponent_side)]))

# ------------------------------------------------------------
# * Preliminaries
# ------------------------------------------------------------

if par['debug']:
    o.data['subject'] = 'test'
else:
    o.get_subject_id('Decision-Making')

o.start_clock()

# ------------------------------------------------------------
# * The main task
# ------------------------------------------------------------

for trial in range(len(opponent_choices)):
    do_trial(trial)

# ------------------------------------------------------------
# * Done
# ------------------------------------------------------------

o.done(par['output_path_fmt'].format(**o.data))

o.wait_screen(1,
    o.text(0, 0, 'Done!\n\nPlease let the experimenter know you are done.'))
