"""
First, a welcoming text, 'Welcome! We show some Symbols. Press SPACE to continue' is shown until
the participant presses the Spacebar. Then a square in purple is followed by a triangle in red
followed by a circle in green. All of these symbols are shown for 3000ms or until the participant
presses the key f or j. The correct key for the purple square and the red triangle is f, and
the correct key for the green circle is j.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import SymbolStimulus, TextStimulus

# EVENT SEQUENCE

stim_1 = TextStimulus(
    text="Welcome! We show some Symbols. Press SPACE to continue",
    choices=[" "],
)

stim_2 = SymbolStimulus(
    duration=3000, symbol="square", color="#f0f", choices=["f", "j"], correct_key="f"
)

stim_3 = SymbolStimulus(
    duration=3000, symbol="triangle", color="red", choices=["f", "j"], correct_key="f"
)

stim_4 = SymbolStimulus(
    duration=3000, symbol="circle", color="green", choices=["f", "j"], correct_key="j"
)

event_sequence = [stim_1, stim_2, stim_3, stim_4]

# BLOCK DESIGN

trial_sequence = Block(event_sequence)
experiment = Experiment([trial_sequence])
experiment.to_html("basic.html")
