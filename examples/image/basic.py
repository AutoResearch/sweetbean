from sweetbean.stimulus import ImageStimulus
from sweetbean.sequence import Block, Experiment

stim_1 = ImageStimulus(
    src='test.png',
    choices=[' '],
)

trial_sequence = Block([stim_1])
experiment = Experiment([trial_sequence])
experiment.to_html('basic.html')

