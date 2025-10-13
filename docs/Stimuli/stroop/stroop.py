"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen. The fixation cross is shown for 1000ms. The soa and iti durations are indicated by
the experimental design. The color of the Stroop task and its words are also indicated by the
experimental design. The correct response  to a red word is f, and the correct response to a
green word is j.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Text
from sweetbean.variable import DataVariable, FunctionVariable, TimelineVariable

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
    if color.lower() == word.lower():
        return "f"
    return "j"


correct_key = FunctionVariable("correct_key", correct_key_fct, [color, word])

last_correct = DataVariable("correct", 1)

feedback_text = FunctionVariable(
    "feedback_text",
    lambda lc: "Correct!" if lc else "False!",
    [last_correct],
)

fixation = Text(800, "+")
so_s = Text(so_s_duration)
stroop = Text(2000, word, color, choices=["f", "j"], correct_key=correct_key)
feedback = Text(800, feedback_text)
so_f = Text(so_f_duration)

# BLOCK DESIGN

block = Block([fixation, so_s, stroop, feedback, so_f], timeline)

# Create an image of the stimuli sequence of the block
block.to_image(
    "stroop.png",
    data=[None, None, {"correct": True}, None, None],
    zoom_factor=3,
    sequence=True,
)

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("feedback_manual.html")
