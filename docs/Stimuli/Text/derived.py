"""
A fixation cross is followed by a blank screen, followed by a Stroop stimulus, followed by another
blank screen.  The fixation cross is shown for 1000ms. The first blank screen is shown for 800ms
the second for 300ms. The Stroop stimulus is shown for 2000ms. This is a task-switching experiment.
The shape of the fixation cross determines the task. An 'x indicates a word reading task, and a '+'
indicates the color naming task. The color of the Stroop task and its word are indicated by a
timeline, as is the task. In the word reading task, the correct response to "RED" is pressing f,
and to "GRREN" is pressing j. Similarly, the correct response to a red word in the color naming
task is f, and the correct response to a green word is j.
"""


from sweetbean.parameter import DerivedLevel, DerivedParameter, TimelineVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus

timeline = [
    {"color": "red", "word": "RED", "task": "color_naming"},
    {"color": "green", "word": "GREEN", "task": "color_naming"},
    {"color": "green", "word": "RED", "task": "word_reading"},
    {"color": "red", "word": "GREEN", "task": "word_reading"},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])
task = TimelineVariable("task", ["color_naming", "word_reading"])


def is_fixation_x(task):
    return task == "word_reading"


def is_fixation_plus(task):
    return task == "color_naming"


x_shape = DerivedLevel("x", is_fixation_x, [task])
plus_shape = DerivedLevel("+", is_fixation_plus, [task])

fixation_shape = DerivedParameter("fixation_shape", [x_shape, plus_shape])


def is_correct_f(word, color, task):
    return (task == "word_reading" and word == "RED") or (
        task == "color_naming" and color == "red"
    )


def is_correct_j(word, color, task):
    return not is_correct_f(word, color, task)


j_key = DerivedLevel("j", is_correct_j, [word, color, task])
f_key = DerivedLevel("f", is_correct_f, [word, color, task])

correct_key = DerivedParameter("correct", [j_key, f_key])

fixation = TextStimulus(1000, fixation_shape)
so_s = TextStimulus(800)
stroop = TextStimulus(2000, word, color, ["j", "g"], correct_key)
so_f = TextStimulus(300)

event_sequence = [fixation, so_s, stroop, so_f]

# BLOCK DESIGN

train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])

experiment.to_autora("package.json", "main.js")
