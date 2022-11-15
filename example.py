from sweetbean.primitives import SimpleStimulus, TimelineVariable, TrialSequence, DerivedLevel, DerivedParameter
from sweetbean import TrialBlock, Experiment

train_sequence = TrialSequence(
    [{'task': 'word_reading', 'word': 'red', 'color': 'red', 'correct': 'f', 'soa': 2000},
     {'task': 'color_naming', 'word': 'green', 'color': 'green', 'correct': 'j',
      'soa': 1000}])

experiment_sequence = TrialSequence(
    [{'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500}])

## STIMULI

soa = SimpleStimulus(duration=TimelineVariable('soa'))
stroop = SimpleStimulus(duration=1500, v_shape=TimelineVariable('word'), v_color=TimelineVariable('color'))


## CONDITIONAL STIMULI
# determine the shape of the fixation (x if word_reading, y if color_naming)
def is_x(task):
    return task == 'word_reading'


def is_plus(task):
    return task == 'color_naming'


x_shape = DerivedLevel('x', is_x, [TimelineVariable('task')])
plus_shape = DerivedLevel('+', is_plus, [TimelineVariable('task')])

fixation_shape = DerivedParameter([x_shape, plus_shape])

fixation = SimpleStimulus(duration=500, v_shape=fixation_shape)


# determine the correct answer
def is_f(task):
    return (task == 'word_reading' and task == 'green') or \
           (task == 'color_naming' and task == 'green')


def is_j(task):
    not (is_f(task))


f_letter = DerivedLevel('f', is_f, [TimelineVariable('task')])
j_letter = DerivedLevel('j', is_j, [TimelineVariable('task')])

correct_letter = DerivedParameter([f_letter, j_letter])

stroop = SimpleStimulus(duration=1500, v_shape=TimelineVariable('word'), v_color=TimelineVariable('color'),
                        correct=correct_letter)

## TRIAL BLOCK

train_block = TrialBlock([fixation, soa, stroop], train_sequence)

experiment_block = TrialBlock([fixation, soa, stroop], experiment_sequence)

## experiment

experiment = Experiment([train_block, experiment_block])

text = experiment.to_psych()

with open('test.js', 'w') as f:
    f.write(text)
