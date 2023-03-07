from sweetbean.stimulus import TextStimulus, SymbolStimulus
from sweetbean.sequence import Block, Experiment

stim_1 = TextStimulus(
    text='Welcome! We show some Symbols. Press SPACE to continue',
    choices=[' '],
)

stim_2 = SymbolStimulus(
    duration=3000,
    symbol='square',
    color='#f0f',
    choices=['f', 'j'],
    correct_key=['f']
)

stim_3 = SymbolStimulus(
    duration=3000,
    symbol='triangle',
    color='red',
    choices=['f', 'j'],
    correct_key=['f']
)

stim_4 = SymbolStimulus(
    duration=3000,
    symbol='circle',
    color='green',
    choices=['f', 'j'],
    correct_key=['j']
)

trial_sequence = Block([stim_1, stim_2, stim_3, stim_4])
experiment = Experiment([trial_sequence])
experiment.to_html('basic.html')

