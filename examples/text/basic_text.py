from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus

text = TextStimulus(
    duration=2000, text="press a or b or wait", color="pink", choices=["a", "b"]
)

block = Block([text])
experiment = Experiment([block])

experiment.to_html("basic.html")
