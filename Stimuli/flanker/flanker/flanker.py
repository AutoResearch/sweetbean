from sweetbean import Block, Experiment
from sweetbean.stimulus import Blank, Feedback, Fixation, Flanker
from sweetbean.variable import TimelineVariable

timeline = [
    {"direction": "left", "distractor": "right", "correct_key": "f"},
    {"direction": "right", "distractor": "right", "correct_key": "j"},
    {"direction": "left", "distractor": "left", "correct_key": "f"},
    {"direction": "right", "distractor": "left", "correct_key": "j"},
]

direction = TimelineVariable("direction")
distractor = TimelineVariable("distractor")
correct_key = TimelineVariable("correct_key")

fixation = Fixation(1000)
so_s = Blank(400)
flanker = Flanker(2000, direction, distractor, ["j", "f"], correct_key)
so_f = Blank(300)
feedback = Feedback(800, window=2)

block = Block([fixation, so_s, flanker, so_f, feedback], timeline)

# Create an image of the stimuli sequence of the block
block.to_image(
    "flanker.png",
    data=[None, None, {"correct": True}, None, None],
    zoom_factor=[3, 3, 1, 3, 3],
    sequence=True,
)

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("flanker.html")
