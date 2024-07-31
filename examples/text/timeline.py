"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen. The fixation cross is shown for 1000ms. The soa and iti durations are indicated by
the experimental design. The color of the Stroop task and its words are also indicated by the
experimental design. The correct response  to a red word is f, and the correct response to a
green word is j.
"""

from sweetbean.parameter import DerivedLevel, DerivedParameter, TimelineVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus

timeline = [
    {"color": "red", "word": "RED", "so_s": 200, "so_f": 1000},
    {"color": "green", "word": "GREEN", "so_s": 1000, "so_f": 100},
    {"color": "green", "word": "RED", "so_s": 100, "so_f": 2000},
    {"color": "red", "word": "GREEN", "so_s": 1000, "so_f": 1000},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])
so_s_duration = TimelineVariable("so_s", [100, 200, 1000])
so_f_duration = TimelineVariable("so_f", [100, 1000, 2000])


def is_correct_f(color):
    return color == "red"


def is_correct_j(color):
    return not is_correct_f(word)


j_key = DerivedLevel("j", is_correct_j, [color])
f_key = DerivedLevel("f", is_correct_f, [color])

correct_key = DerivedParameter("correct", [j_key, f_key])

fixation = TextStimulus(800, "+")
so_s = TextStimulus(so_s_duration)
stroop = TextStimulus(2000, word, color, ["f", "j"], correct_key)
so_f = TextStimulus(so_f_duration)

event_sequence = [fixation, so_s, stroop, so_f]

# BLOCK DESIGN

train_block = Block([fixation, so_s, stroop, so_f], timeline)
experiment = Experiment([train_block])

experiment.to_html("timeline.html")
