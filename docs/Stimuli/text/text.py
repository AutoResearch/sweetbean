"""
The text 'press a or b or wait' is shown in pink for 2000ms. The allowed responses are 'a' and 'b'.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Text

# EVENT SEQUENCE

text = Text(
    duration=2000, text="press a or b or wait", color="pink", choices=["a", "b"]
)


event_sequence = [text]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])

experiment.to_html("text.html")
