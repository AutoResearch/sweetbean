"""
First, a welcoming text, 'Welcome! We show some Symbols. Press SPACE to continue' is shown until
the participant presses the Spacebar. Then a square in purple is followed by a triangle in red
followed by a circle in green. All of these symbols are shown for 3000ms or until the participant
presses the key f or j. The correct key for the purple square and the red triangle is f, and
the correct key for the green circle is j.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Symbol, Text

# EVENT SEQUENCE

stim_1 = Text(
    text="Welcome! We show some Symbols. Press SPACE to continue",
    choices=[" "],
)

stim_2 = Symbol(
    duration=3000, symbol="square", color="#f0f", choices=["f", "j"], correct_key="f"
)

stim_3 = Symbol(
    duration=3000, symbol="triangle", color="red", choices=["f", "j"], correct_key="f"
)

stim_4 = Symbol(
    duration=3000, symbol="circle", color="green", choices=["f", "j"], correct_key="j"
)

event_sequence = [stim_1, stim_2, stim_3, stim_4]

# BLOCK DESIGN

block = Block(event_sequence)

# Create an image of the stimuli sequence of the block
block.to_image(path="symbols.png", data=None, zoom_factor=[1, 3, 3, 3])

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("symbols.html")
