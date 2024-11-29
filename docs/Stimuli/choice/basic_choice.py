from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import ChoiceStimulus

stim_1 = ChoiceStimulus()

trial_sequence = Block([stim_1])
experiment = Experiment([trial_sequence])
experiment.to_html("basic.html")
