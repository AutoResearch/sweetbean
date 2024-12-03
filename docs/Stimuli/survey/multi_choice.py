"""
After the participant is greeted with 'Welcome! We show a survey. Press SPACE to continue' until
they press the spacebar, they are asked two multiple-choice questions. One is about how they are,
which they can rate as bad, good, or fine. The other is about their handedness.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import MultiChoiceSurvey, Text

# EVENT SEQUENCE

stim_1 = Text(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = MultiChoiceSurvey(
    questions=[
        {"prompt": "How are you?", "options": ["bad", "good", "fine"]},
        {
            "prompt": "What is your handedness?",
            "options": ["left", "right", "other", "prefer not to say"],
        },
    ]
)

event_sequence = [stim_1, stim_2]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])
experiment.to_html("multi_choice.html")
