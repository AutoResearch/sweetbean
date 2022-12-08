from sweetbean.primitives import TextStimulus, TimelineVariable, TrialSequence, DerivedLevel, DerivedParameter, \
    FeedbackStimulus, FlankerStimulus, SymbolStimulus, BlankStimulus
from sweetbean import TrialBlock, Experiment

######## HERE STARTS THE  *** SWEETBEAN *** CODE

## STIMULI


def is_x(task):
    return task == 'word_reading'


def is_plus(task):
    return task == 'color_naming'


x_shape = DerivedLevel('x', is_x, [TimelineVariable('task', ['word_reading', 'color_naming'])])
plus_shape = DerivedLevel('+', is_plus, [TimelineVariable('task', ['word_reading', 'color_naming'])])

def is_f(task, color):
    return (task == 'word_reading' and color == 'green') or \
           (task == 'color_naming' and color == 'green')


def is_j(task, color):
    return not is_f(task, color)


f_letter = DerivedLevel('f', is_f, [TimelineVariable('task', ['word_reading', 'color_naming']),
                                    TimelineVariable('color', ['red', 'green'])])
j_letter = DerivedLevel('j', is_j, [TimelineVariable('task', ['word_reading', 'color_naming']),
                                    TimelineVariable('color', ['red', 'green'])])

correct_letter = DerivedParameter('correct', [f_letter, j_letter])

fixation_shape = DerivedParameter("fixation_shape", [x_shape, plus_shape])

test = TextStimulus(duration=500, text=fixation_shape, choices=['j', 'f'], correct=correct_letter)

#
# feedback = FeedbackStimulus(duration=2000, kind='screen')
# symbol = SymbolStimulus(duration=2000, symbol=TimelineVariable('symbol'), color=TimelineVariable('color'))
#
#
# ## CONDITIONAL STIMULI
# # determine the shape of the fixation (x if word_reading, y if color_naming)
#
#
#
# # determine the correct answer

#
# stroop = TextStimulus(duration=1500, text=TimelineVariable('word'), color=TimelineVariable('color'),
#                       correct=correct_letter, choices=['j', 'f'])
#
#
# def is_distractor_left(direction, congruency):
#     return (direction == 'left' and congruency == 'congruent') or \
#            (direction == 'right' and congruency == 'incongruent')
#
#
# def is_distractor_right(direction, congruency):
#     return not is_distractor_left(direction, congruency)
#
#
# dist_left = DerivedLevel('left', is_distractor_left, [TimelineVariable('direction', ['left', 'right']),
#                                                       TimelineVariable('congruency', ['congruent', 'incongruent'])])
# dist_right = DerivedLevel('right', is_distractor_right, [TimelineVariable('direction', ['left', 'right']),
#                                                          TimelineVariable('congruency', ['congruent', 'incongruent'])])
#
# distractor = DerivedParameter('distractor', [dist_left, dist_right])
#
# flanker = FlankerStimulus(duration=2000, direction=TimelineVariable('direction'), correct=TimelineVariable('correct'),
#                           distractor=distractor, choices=['j', 'f'])
#
# blank = BlankStimulus(duration=2000, correct='j', choices=['j', 'f'])
## TRIAL BLOCK

train_block = TrialBlock([test])

# experiment_block = TrialBlock([fixation, soa, stroop, feedback], experiment_sequence)

## experiment

experiment = Experiment([train_block])

##### HERE STOPS THE *** SWEETBEAN *** CODE

text = experiment.to_psych()

with open('test.js', 'w') as f:
    f.write(text)
