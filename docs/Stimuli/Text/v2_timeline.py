"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen. The fixation cross is shown for 1000ms. The soa and iti durations are indicated by
the experimental design. The color of the Stroop task and its words are also indicated by the
experimental design. The correct response  to a red word is f, and the correct response to a
green word is j.
"""

from sweetbean_v2 import Block, Experiment
from sweetbean_v2.datatype.variables import TimelineVariable
from sweetbean_v2.stimulus import Text

timeline = [
    {"color": "red", "word": "RED", "so_s": 200, "so_f": 1000},
    {"color": "green", "word": "GREEN", "so_s": 1000, "so_f": 100},
    {"color": "green", "word": "RED", "so_s": 100, "so_f": 2000},
    {"color": "red", "word": "GREEN", "so_s": 1000, "so_f": 1000},
]

# EVENT SEQUENCE

color = TimelineVariable("color")
word = TimelineVariable("word")
so_s_duration = TimelineVariable("so_s")
so_f_duration = TimelineVariable("so_f")

fixation = Text(800, "+")
so_s = Text(so_s_duration)
stroop = Text(2000, word, color)
so_f = Text(so_f_duration)

event_sequence = [fixation, so_s, stroop, so_f]

# BLOCK DESIGN

train_block = Block([fixation, so_s, stroop, so_f], timeline)
experiment = Experiment([train_block])

experiment.to_html("timeline.html")
