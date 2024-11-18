"""
After the participant is greeted with 'Welcome! We show a survey. Press SPACE to continue' until
they press the spacebar, they are asked free-from questions about how old they are, their gender,
and their handedness.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus, TextSurveyStimulus

# EVENT SEQUENCE

stim_1 = TextStimulus(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = TextSurveyStimulus(
    prompts=["How old are you?", "What is your gender?", "What is your handedness?"]
)

event_sequence = [stim_1, stim_2]

# BLOCK DESIGN

trial_sequence = Block(event_sequence)
experiment = Experiment([trial_sequence])
experiment.to_html("text.html")
