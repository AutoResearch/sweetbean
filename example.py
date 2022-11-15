from sweetbean.primitives import SimpleStimulus, TimelineVariable, TrialSequence
from sweetbean import TrialBlock, Experiment

train_sequence = TrialSequence([{'word': 'red', 'color': 'red', 'correct': 'f', 'soa': 2000},
                                {'word': 'green', 'color': 'green', 'correct': 'j', 'soa': 1000}])

experiment_sequence = TrialSequence([{'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
                                {'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500}])

## STIMULI

fixation = SimpleStimulus(duration=500, v_shape='x')
soa = SimpleStimulus(duration=TimelineVariable('soa'))
stroop = SimpleStimulus(duration=1500, v_shape=TimelineVariable('word'), v_color=TimelineVariable('color'))



## TRIAL BLOCK

train_block = TrialBlock([fixation, soa, stroop], train_sequence)


experiment_block = TrialBlock([fixation, soa, stroop], experiment_sequence)

## experiment

experiment = Experiment([train_block, experiment_block])

text = experiment.to_psych()

with open('test.js', 'w') as f:
    f.write(text)
