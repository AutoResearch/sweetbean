# -*- coding: utf-8 -*-
""" Weber Fechner

An example for Weber Fechner.  Here, we have a simple stimulus timeline:
[fixation, blank, rdp, blank, feedback]

"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Blank, Feedback, Fixation, RandomDotPatterns
from sweetbean.variable import TimelineVariable

timeline = [
    {"S1": 40, "S2": 70, "correct_key": "y"},
    {"S1": 70, "S2": 70, "correct_key": "n"},
    {"S1": 70, "S2": 40, "correct_key": "y"},
    {"S1": 70, "S2": 70, "correct_key": "n"},
    {"S1": 40, "S2": 70, "correct_key": "y"},
    {"S1": 70, "S2": 40, "correct_key": "y"},
    {"S1": 40, "S2": 40, "correct_key": "n"},
    {"S1": 40, "S2": 40, "correct_key": "n"},
    {"S1": 40, "S2": 40, "correct_key": "n"},
    {"S1": 70, "S2": 40, "correct_key": "y"},
]

fixation = Fixation(800)

blank_1 = Blank(400)
blank_2 = Blank(1000)

s1 = TimelineVariable("S1")
s2 = TimelineVariable("S2")
correct_key = TimelineVariable("correct_key")

# We can use these variables in the stimuli declaration:

rdp = RandomDotPatterns(
    duration=1000,
    number_of_oobs=[s1, s2],
    number_of_apertures=2,
    choices=["y", "n"],
    correct_key=correct_key,
)


feedback = Feedback(500, window=2)

event_sequence = [fixation, blank_1, rdp, blank_2, feedback]

block = Block(event_sequence, timeline)

# Create an image of the stimuli sequence of the block
block.to_image(
    "weber_fechner.png",
    data=[None, None, {"correct": True}, None, None],
    zoom_factor=[3, 3, 1, 3, 3],
    sequence=True,
)

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("weber_fechner.html")
