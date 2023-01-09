from sweetbean.stimulus import TextStimulus
from sweetbean import TrialBlock, Experiment

stim_1 = TextStimulus(
    text='Welcome! This is a Stroop Task. Press SPACE to continue',
    choices=[' '],
)

stim_2 = TextStimulus(
    duration=3000,
    text='RED',
    color='red',
    choices=['f', 'j'],
    correct_key=['f']
)

stim_3 = TextStimulus(
    duration=3000,
    text='GREEN',
    color='red',
    choices=['f', 'j'],
    correct_key=['f']
)

stim_4 = TextStimulus(
    duration=3000,
    text='RED',
    color='green',
    choices=['f', 'j'],
    correct_key=['j']
)



trial_sequence = TrialBlock([stim_1, stim_2, stim_3, stim_4])
experiment = Experiment([trial_sequence])
experiment.to_html('index.html')

