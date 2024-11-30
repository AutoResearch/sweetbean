"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen. The fixation cross is shown for 1000ms. The soa and iti durations are indicated by
the experimental design. The color of the Stroop task and its words are also indicated by the
experimental design. The correct response  to a red word is f, and the correct response to a
green word is j.
"""

from sweetbean_v2 import Block, Experiment
from sweetbean_v2.datatype.variables import TimelineVariable
from sweetbean_v2.stimulus import Flanker

timeline = [
    {"target": "left", "distractor": "right"},
]

# EVENT SEQUENCE

target = TimelineVariable("target")
distractor = TimelineVariable("distractor")

flanker = Flanker(2000, target, distractor)

# BLOCK DESIGN

train_block = Block([flanker], timeline)
experiment = Experiment([train_block])

experiment.to_html("timeline.html")
