from sweetbean.parameter import CodeVariable
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import ImageStimulus

stim_1 = ImageStimulus(
    src="test.png",
    choices=[" "],
)

trial_sequence = Block([stim_1], CodeVariable("condition[0]"))
experiment = Experiment([trial_sequence])
experiment.to_html("basic.html")
