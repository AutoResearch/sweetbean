"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen. The fixation cross is shown for 1000ms. The soa and iti durations are indicated by
the experimental design. The color of the Stroop task and its words are also indicated by the
experimental design. The correct response  to a red word is f, and the correct response to a
green word is j.
"""

from sweetbean_v2 import Block, Experiment
from sweetbean_v2.datatype.variables import FunctionVariable, TimelineVariable
from sweetbean_v2.stimulus import Feedback, Text

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


def correct_key_fct(color, word):

    if color == word:
        return "f"
    return "j"


x = "red"

correct_key = FunctionVariable("correct_key", correct_key_fct, [color, x])

false_feedback = FunctionVariable(
    "correct_feedback",
    lambda col, key: f"The color was {col} you supposed to press {key}",
    [color, correct_key],
)


fixation = Text(800, "+")
so_s = Text(so_s_duration)
stroop = Text(2000, word, color, choices=["f", "j"], correct_key=correct_key)
feedback = Feedback(800, false_message=false_feedback)
so_f = Text(so_f_duration)

# BLOCK DESIGN

train_block = Block([fixation, so_s, stroop, feedback, so_f], timeline)
experiment = Experiment([train_block])

experiment.to_html("timeline.html")
