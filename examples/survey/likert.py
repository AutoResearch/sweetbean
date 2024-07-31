"""
A welcoming text the participant is shown until the participant presses the spacebar. The text says,
'Welcome! We show a survey. Press SPACE to continue'. This is followed by a survey with two
questions that the participant is supposed to answer on a likert scale. The first question is
'How are you feeling?' and the participant is supposed to rate their feeling on a scale from
-2 to 2 with 5 levels. The second question is 'Do you like this tool?' on a scale from 1 to 3.
Then, the participant is supposed to rate five animals on their cuteness from 1 to 5.
The animals are a bunny, a shark, a spider, a cat, and a dog.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import LikertSurveyStimulus, TextStimulus

# EVENT SEQUENCE

stim_1 = TextStimulus(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = LikertSurveyStimulus(
    prompts=[
        {"How are you feeling?": [-2, -1, 0, 1, 2]},
        {"Do you like this tool?": [0, 1, 3]},
    ]
)

stim_3 = TextStimulus(
    text="Rate the following animals on a scale from 1-5 on their cuteness.",
    choices=[" "],
)

stim_4 = LikertSurveyStimulus.from_scale(
    prompts=["bunny", "shark", "spider", "cat", "dog"], scale=[1, 2, 3, 4, 5]
)

event_sequence = [stim_1, stim_2, stim_3, stim_4]

# BLOCK DESIGN

trial_sequence = Block(event_sequence)
experiment = Experiment([trial_sequence])
experiment.to_html("likert.html")
