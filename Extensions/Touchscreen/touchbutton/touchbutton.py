from sweetbean import Block, Experiment
from sweetbean.extension import TouchButton
from sweetbean.stimulus import Blank, Feedback, Fixation, Flanker
from sweetbean.variable import FunctionVariable, TimelineVariable

timeline = [
    {"direction": "left", "distractor": "right", "correct_key": "f"},
    {"direction": "right", "distractor": "right", "correct_key": "j"},
    {"direction": "left", "distractor": "left", "correct_key": "f"},
    {"direction": "right", "distractor": "left", "correct_key": "j"},
]

direction = TimelineVariable("direction")
distractor = TimelineVariable("distractor")
correct_key = FunctionVariable(
    "correct_key",
    lambda dir: TouchButton.left() if dir == "left" else TouchButton.right(),
    [TimelineVariable("direction")],
)

fixation = Fixation(1000)
so_s = Blank(400)
flanker = Flanker(
    2000, direction, distractor, [TouchButton.left(), TouchButton.right()], correct_key
)
so_f = Blank(300)
feedback = Feedback(800, window=2)

block = Block([fixation, so_s, flanker, so_f, feedback], timeline)

# Create an image of the stimuli sequence of the block


# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("touchButton.html")
