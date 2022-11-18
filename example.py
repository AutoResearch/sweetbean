from sweetbean.primitives import TextStimulus, TimelineVariable, TrialSequence, DerivedLevel, DerivedParameter, Feedback, FlankerStimulus
from sweetbean import TrialBlock, Experiment

train_sequence = TrialSequence(
    [{'task': 'word_reading', 'word': 'red', 'color': 'red', 'correct': 'f', 'soa': 2000, 'direction':'left', 'congruency':'congruent'},
     {'task': 'color_naming', 'word': 'green', 'color': 'green', 'correct': 'j', 'soa': 1000, 'direction':'right','congruency':'incocngruent'},
     {'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500, 'direction':'right', 'congruency':'incongruent'},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500, 'direction':'left', 'congruency':'congruent'},
     {'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500, 'direction':'right', 'congruency':'incongruent'},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500, 'direction':'left', 'congruency':'congruent'},
     ])

experiment_sequence = TrialSequence(
    [{'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500},
     {'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500},
     {'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500},
     {'task': 'word_reading', 'word': 'green', 'color': 'red', 'correct': 'j', 'soa': 500},
     {'task': 'color_naming', 'word': 'red', 'color': 'green', 'correct': 'f', 'soa': 1500},
     ])

######## HERE STARTS THE  *** SWEETBEAN *** CODE

## STIMULI

soa = TextStimulus(duration=TimelineVariable('soa'))
feedback = Feedback(duration=800)


## CONDITIONAL STIMULI
# determine the shape of the fixation (x if word_reading, y if color_naming)
def is_x(task):
    return task == 'word_reading'
def is_plus(task):
    return task == 'color_naming'


x_shape = DerivedLevel('x', is_x, [TimelineVariable('task')])
plus_shape = DerivedLevel('+', is_plus, [TimelineVariable('task')])

fixation_shape = DerivedParameter("fixation_shape" ,[x_shape, plus_shape])

fixation = TextStimulus(duration=500, text=fixation_shape)


# determine the correct answer
def is_f(task):
    return (task == 'word_reading' and task == 'green') or \
           (task == 'color_naming' and task == 'green')

def is_j(task):
    return not is_f(task)


f_letter = DerivedLevel('f', is_f, [TimelineVariable('task')])
j_letter = DerivedLevel('j', is_j, [TimelineVariable('task')])

correct_letter = DerivedParameter('correct',[f_letter, j_letter])

stroop = TextStimulus(duration=1500, text=TimelineVariable('word'), color=TimelineVariable('color'),
                        correct=correct_letter, choices=['j', 'f'])

def is_distractor_left(direction, congruency):
    return (direction == 'left' and congruency == 'congruent') or \
           (direction == 'right' and congruency == 'incongruent')
def is_distractor_right(direction, congruency):
    return not is_distractor_left(direction, congruency)

dist_left = DerivedLevel('left', is_distractor_left, [TimelineVariable('direction'), TimelineVariable('congruency')])
dist_right = DerivedLevel('right', is_distractor_right, [TimelineVariable('direction'), TimelineVariable('congruency')])

distractor = DerivedParameter('distractor', [dist_left, dist_right])

flanker = FlankerStimulus(duration=2000, direction=TimelineVariable('direction'), correct=TimelineVariable('correct'),
                          distractor=distractor, choices=['j', 'f'])
## TRIAL BLOCK

train_block = TrialBlock([fixation, flanker, feedback], train_sequence)

#experiment_block = TrialBlock([fixation, soa, stroop, feedback], experiment_sequence)

## experiment

experiment = Experiment([train_block])

##### HERE STOPS THE *** SWEETBEAN *** CODE

text = experiment.to_psych()

with open('test.js', 'w') as f:
    f.write(text)

# JEPS LEARNING, MEMORY AND COGNITION