from sweetbean_v2 import Block, Experiment
from sweetbean_v2.stimulus import Text

text = Text(
    duration=2000, text="press a or b or wait", color="pink", choices=["a", "b"]
)

event_sequence = [text]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])

experiment.to_html("basic.html")
