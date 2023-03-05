from sweetbean.stimulus import TextStimulus
from sweetbean.sequence import Block, Experiment


stroop = TextStimulus(text='hi<br>how')
fixation = TextStimulus(duration=800, text='+')
stroop = TextStimulus(duration=2000, )

train_block = Block([stroop])
experiment = Experiment([train_block])

experiment.to_html('index.html')
