"""
(only in pr-release)
An instructions screen welcoming the participant to the experiment,
followed by a second page of instructions, and a final page of instructions.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Generic

instructions = Generic(
    type="jsPsychInstructions",
    pages=[
        "Welcome to the experiment",
        "This is the second page of instructions",
        "This is the final page",
    ],
    show_clickable_nav=True,
)

block = Block([instructions])

experiment = Experiment([block])
experiment.to_html("instructions.html")
