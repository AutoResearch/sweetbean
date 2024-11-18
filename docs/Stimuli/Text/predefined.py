from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import (
    BlankStimulus,
    FeedbackStimulus,
    FixationStimulus,
    FlankerStimulus,
)

timeline = [
    {"direction": "left", "distractor": "right", "correct_key": "f"},
    {"direction": "right", "distractor": "right", "correct_key": "j"},
    {"direction": "left", "distractor": "left", "correct_key": "f"},
    {"direction": "right", "distractor": "left", "correct_key": "j"},
]

direction = TimelineVariable("direction", ["left", "right"])
distractor = TimelineVariable("distractor", ["left", "right"])
correct_key = TimelineVariable("correct_key", ["j", "f"])

fixation = FixationStimulus(1000)
so_s = BlankStimulus(400)
flanker = FlankerStimulus(2000, direction, distractor, ["j", "f"], correct_key)
so_f = BlankStimulus(300)
feedback = FeedbackStimulus(800, 2)

train_block = Block([fixation, so_s, flanker, so_f, feedback], timeline)
experiment = Experiment([train_block])

experiment.to_html("predefined.html")
