"""
After the participant is greeted with 'Welcome! We show a survey. Press SPACE to continue' until
they press the spacebar, they are asked free-from questions about how old they are, their gender,
and their handedness.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Text, TextSurvey

# EVENT SEQUENCE

stim_1 = Text(
    text="Welcome! We show a survey. Press SPACE to continue",
    choices=[" "],
)

stim_2 = TextSurvey(
    questions=["How old are you?", "What is your gender?", "What is your handedness?"]
)

event_sequence = [stim_1, stim_2]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])
experiment.to_html("text_survey.html")
