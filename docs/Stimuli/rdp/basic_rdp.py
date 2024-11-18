"""
Two dot patterns are shown with a different number of dots for 2000ms.
The number of dots is given by the experimental design.
"""

from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import FeedbackStimulus, RandomDotPatternsStimulus

timeline = [
    {"intensities": [90, 100], "correct_key": "y"},
    {"intensities": [90, 90], "correct_key": "n"},
    {"intensities": [10, 20], "correct_key": "y"},
    {"intensities": [100, 90], "correct_key": "y"},
    {"intensities": [10, 10], "correct_key": "n"},
    {"intensities": [20, 20], "correct_key": "y"},
    {"intensities": [100, 100], "correct_key": "n"},
    {"intensities": [20, 20], "correct_key": "n"},
]

# EVENT SEQUENCE
intensities = TimelineVariable(
    "intensities",
    [[90, 100], [90, 90], [10, 20], [100, 90], [20, 20], [100, 100], [10, 10]],
)

correct_key = TimelineVariable("correct_key", ["y", "n"])

rok = RandomDotPatternsStimulus(
    duration=2000,
    number_of_oobs=intensities,
    number_of_apertures=2,
    choices=["y", "n"],
    correct_key=correct_key,
)

feedback = FeedbackStimulus(500)
event_sequence = [rok, feedback]

# BLOCK DESIGN

block = Block(event_sequence, timeline)
experiment = Experiment([block])

experiment.to_html("rok_weber_fechner.html")
