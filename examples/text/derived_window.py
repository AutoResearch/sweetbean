"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen, followed by feedback. The fixation cross is shown for 1000ms. The first blank screen
is shown for 400ms the second for 300ms. The Stroop stimulus is shown for 2000ms. Feedback is shown
for 800ms. This is a task-switching experiment. The color of the Stroop task and its words are
indicated by the experimental design. The correct response  to a red word in the color naming task
is f, and the correct response to a green word is j. If the participant's response was correct,
the text "correct" is shown. If the participant's response was false, the text "false" is shown.
"""

from sweetbean.parameter import (
    DataVariable,
    DerivedLevel,
    DerivedParameter,
    TimelineVariable,
)
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus

timeline = [
    {"color": "red", "word": "RED", "correct_key": "f"},
    {"color": "green", "word": "GREEN", "correct_key": "j"},
    {"color": "green", "word": "RED", "correct_key": "f"},
    {"color": "red", "word": "GREEN", "correct_key": "j"},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])


def is_correct_f(color):
    return color == "red"


def is_correct_j(color):
    return not is_correct_f(word)


j_key = DerivedLevel("j", is_correct_j, [color])
f_key = DerivedLevel("f", is_correct_f, [color])

correct_key = DerivedParameter("correct", [j_key, f_key])

# Creating a data variable
correct = DataVariable("correct", [True, False])


# Predicates
def is_correct(correct):
    return correct


def is_false(correct):
    return not correct


# Derived Levels
correct_feedback = DerivedLevel("correct", is_correct, [correct], 2)
false_feedback = DerivedLevel("false", is_false, [correct], 2)

# Derived Parameter
feedback_text = DerivedParameter("feedback_text", [correct_feedback, false_feedback])

# Using it in the stimulus
fixation = TextStimulus(1000, "+")
so_s = TextStimulus(400)
stroop = TextStimulus(2000, word, color, ["j", "f"], correct_key)
so_f = TextStimulus(300)
feedback = TextStimulus(800, feedback_text)

event_sequence = [fixation, so_s, stroop, so_f, feedback]

# BLOCK DESIGN

train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])

experiment.to_html("derived_window.html")
