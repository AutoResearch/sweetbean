"""
A welcoming text the participant is shown until the participant presses the spacebar. The text says,
'Welcome! We show a survey. Press SPACE to continue'. This is followed by a survey with two
questions that the participant is supposed to answer on a likert scale. The first question is
'How are you feeling?' and the participant is supposed to rate their feeling on a scale from
-2 to 2 with 5 levels. The second question is 'Do you like this tool?' on a scale from 1 to 3.
Then, the participant is supposed to rate five animals on their cuteness from 1 to 5.
The animals are a bunny, a shark, a spider, a cat, and a dog.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import LikertSurvey, Text

# EVENT SEQUENCE

stim_1 = Text(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = LikertSurvey(
    questions=[
        {"prompt": "How are you feeling?", "labels": [-2, -1, 0, 1, 2]},
        {"prompt": "Do you like this tool?", "labels": [0, 1, 3]},
    ]
)

stim_3 = Text(
    text="Rate the following animals on a scale from 1-5 on their cuteness.",
    choices=[" "],
)

stim_4 = LikertSurvey.from_scale(
    prompts=["bunny", "shark", "spider", "cat", "dog"], scale=[1, 2, 3, 4, 5]
)

event_sequence = [stim_1, stim_2, stim_3, stim_4]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])
experiment.to_html("likert.html")
