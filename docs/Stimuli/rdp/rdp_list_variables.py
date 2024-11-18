# -*- coding: utf-8 -*-
""" Weber Fechner

An example for Weber Fechner.  Here, we have a simple stimulus timeline:
[fixation, blank, rdp, blank]

"""

from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import (
    BlankStimulus,
    FixationStimulus,
    RandomDotPatternsStimulus,
)

timeline = [
    {"S1": 40, "S2": 70},
    {"S1": 70, "S2": 70},
    {"S1": 70, "S2": 40},
    {"S1": 70, "S2": 70},
    {"S1": 40, "S2": 70},
    {"S1": 70, "S2": 40},
    {"S1": 40, "S2": 40},
    {"S1": 40, "S2": 40},
    {"S1": 40, "S2": 40},
    {"S1": 70, "S2": 40},
]

fixation = FixationStimulus(800)

blank_1 = BlankStimulus(400)
blank_2 = BlankStimulus(1000)

s1 = TimelineVariable("S1", [40, 70])
s2 = TimelineVariable("S2", [40, 70])

# We can use these variables in the stimuli declaration:

rdp = RandomDotPatternsStimulus(
    duration=1000,
    number_of_oobs=[s1, s2],
    number_of_apertures=2,
    choices=["y", "n"],
)

event_sequence = [fixation, blank_1, rdp, blank_2]

block = Block(event_sequence, timeline)

experiment = Experiment([block])

experiment.to_html("rok_weber_fechner.html")
