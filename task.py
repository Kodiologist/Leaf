#!/usr/bin/env python
# encoding: UTF-8

from sys import argv
from time import sleep
from random import randint, sample
from psychopy.event import getKeys, clearEvents
from psychopy.visual import Rect, Line, TextStim, Circle
import schizoidpy
from schizoidpy import StimGroup

par = dict(zip(argv[1::2], argv[2::2])) # DEPLOYMENT SCRIPT EDITS THIS LINE

o = schizoidpy.Task(
    button_radius = .12,
    okay_button_pos = (0, -.7))
o.save('task', par['task'])

trials_per_option_per_block = 20

# ------------------------------------------------------------
# * Declarations
# ------------------------------------------------------------

def shuffled(l):
    return sample(l, len(l))

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

choice_colors = {COOPERATE: 'green', DEFECT: 'blue'}
opponent_choice_color = 'yellow'
choices_by_side = {
    LEFT: COOPERATE, RIGHT: DEFECT,
    UP: COOPERATE, DOWN: DEFECT}

# Running totals
def score_counters(player_score, opponent_score):
    global show_opponent_score
    if show_opponent_score:
        s = ('You:           %4d' % player_score +
             '\nOther player:  %4d' % opponent_score)
    else:
        s = 'Your score:  %4d' % player_score
    return TextStim(o.win, s, color = 'black',
        font = 'Consolas',
        pos = (-.5, .7),
        height = .1)

# Opponent choice boxes
def opponent_choice_boxes(opponent_choices, trial):
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
    marker = Circle(o.win,
        lineColor = 'black', fillColor = opponent_choice_color,
        radius = min(width, height)/4,
        pos = pos(trial))
    return StimGroup(boxes + [marker])

# Payoff matrix
def pmatrix(opponent_side, payoffs):
    x_offset = .3
    y_offset = -.2
    length = 1.
    linewidth = 3
       # lineWidth arguments are in pixels.
    cwidth = length/5
    cheight = cwidth/2
    def gridsquare(hside, vside):
        global show_opponent_score
        x = hside.sign * length/4 + x_offset
        y = vside.sign * length/4 + y_offset
        player_points = payoffs[
            choices_by_side[hside],
            choices_by_side[vside]]
        opponent_points = payoffs[
            choices_by_side[vside],
            choices_by_side[hside]] if show_opponent_score else ''
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
    opponent_marker = Circle(o.win,
        lineColor = 'black', fillColor = opponent_choice_color,
        radius = min(cwidth, cheight)/4,
        pos = (x_offset - length/2 - cwidth/2 - .05,
            y_offset + opponent_side.sign * length/4))
    grayout = Rect(o.win,
        fillColor = 'white', lineColor = None, opacity = .7,
        width = length, height = length/2,
        pos = (x_offset, opponent_side.flip.sign * length/4 + y_offset))
    stims = (
        gridsquare(LEFT, UP) + 
        gridsquare(RIGHT, UP) +
        gridsquare(RIGHT, DOWN) +
        gridsquare(LEFT, DOWN) + [
        card(LEFT, -length/4, length/2 + cheight/2 + .05),
        card(RIGHT, length/4, length/2 + cheight/2 + .05),
        o.text(x_offset, length/2 + y_offset + .3, 'You'),
        card(UP, -length/2 - cwidth/2 - .05, length/4),
        card(DOWN, -length/2 - cwidth/2 - .05, -length/4),
        o.text(x_offset - length/2 - .2, -.2, 'Other\nplayer'),
        grayout,
        opponent_marker])
    player_marker_f = lambda hside, vside: Rect(o.win,
        fillColor = 'yellow', lineColor = None, opacity = .3,
        width = length/2, height = length/2,
        pos =
           (hside.sign * length/4 + x_offset,
            vside.sign * length/4 + y_offset))
    return StimGroup(stims), player_marker_f

def wait_for_keypress(dkey, keys):
    with o.timestamps(dkey):
        while True:
            pressed = getKeys(keys + ['escape'])
            if 'escape' in pressed:
                quit()
            if len(pressed) == 1:
                return pressed[0]
            clearEvents()
            sleep(.1)

def do_trial(payoff_condition, opponent_choices, trial, payoffs):
    global player_score, opponent_score
    dkey = ('payoff_condition', payoff_condition, 'cooperated', trial)
    opponent_choice = opponent_choices[trial]
    opponent_side = UP if choices_by_side[UP] is opponent_choice else DOWN
    oc_boxes = opponent_choice_boxes(opponent_choices, trial)
    pm, pm_player_marker = pmatrix(opponent_side, payoffs)
    o.draw(score_counters(player_score, opponent_score), oc_boxes, pm)
    pressed = wait_for_keypress(dkey, ['left', 'right'])

    chosen_side = LEFT if pressed == 'left' else RIGHT
    player_choice = choices_by_side[chosen_side]
    o.save(dkey, player_choice is COOPERATE)
    player_score += payoffs[player_choice, opponent_choice]
    opponent_score += payoffs[opponent_choice, player_choice]
    o.wait_screen(.5,
        score_counters(player_score, opponent_score),
        oc_boxes, pm,
        pm_player_marker(chosen_side, opponent_side))

# ------------------------------------------------------------
# * Preliminaries
# ------------------------------------------------------------

if par['debug']:
    o.data['subject'] = 'test'
else:
    o.get_subject_id('Decision-Making')

show_opponent_score = bool(randint(0, 1))
o.save('show_opponent_score', show_opponent_score)

payoff_conditions = ['1-2-3-4', '1-2-9-10']
if randint(0, 1):
    payoff_conditions = payoff_conditions[::-1]
o.save('payoff_condition_order', payoff_conditions)

o.start_clock()

# ------------------------------------------------------------
# * The main task
# ------------------------------------------------------------

for payoff_condition in payoff_conditions:
    amounts = [int(s) for s in payoff_condition.split('-')]
    payoffs = {
      # The first element of each pair is the player whose payoffs
      # we're asking about.
        (COOPERATE, DEFECT): amounts[0],
        (DEFECT, DEFECT): amounts[1],
        (COOPERATE, COOPERATE): amounts[2],
        (DEFECT, COOPERATE): amounts[3]}
    opponent_cooperates = shuffled([c for c in (False, True)
        for n in range(trials_per_option_per_block)])
    o.save(('payoff_condition', payoff_condition, 'opponent_cooperates'),
        opponent_cooperates)
    opponent_choices = map(Choice.from_bool, opponent_cooperates)
    player_score = 0
    opponent_score = 0
    for trial in range(len(opponent_choices)):
        do_trial(payoff_condition, opponent_choices, trial, payoffs)
    o.draw(score_counters(player_score, opponent_score),
       o.text(0, 0,
          'Round complete.\n\nPress the spacebar to continue.'))
    wait_for_keypress(('payoff_condition', payoff_condition, 'completion_screen'),
        ['space'])

# ------------------------------------------------------------
# * Done
# ------------------------------------------------------------

o.done(par['output_path_fmt'].format(**o.data))

o.wait_screen(1,
    o.text(0, 0, 'Done!\n\nPlease let the experimenter know you are done.'))
