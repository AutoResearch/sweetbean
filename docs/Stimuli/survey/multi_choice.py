"""
After the participant is greeted with 'Welcome! We show a survey. Press SPACE to continue' until
they press the spacebar, they are asked two multiple-choice questions. One is about how they are,
which they can rate as bad, good, or fine. The other is about their handedness.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import MultiChoiceSurveyStimulus, TextStimulus

# EVENT SEQUENCE

stim_1 = TextStimulus(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = MultiChoiceSurveyStimulus(
    prompts=[
        {"How are you?": ["bad", "good", "fine"]},
        {"What is your handedness?": ["left", "right", "other", "prefer not to say"]},
    ]
)

event_sequence = [stim_1, stim_2]

# BLOCK DESIGN

trial_sequence = Block(event_sequence)
experiment = Experiment([trial_sequence])
experiment.to_html("multi_choice.html")
