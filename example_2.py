from sweetbean.primitives import SymbolStimulus, DerivedLevel, DerivedParameter, TimelineVariable, FixationStimulus, \
    TextStimulus, BlankStimulus, TrialSequence
from sweetbean import TrialBlock, Experiment

sequence = TrialSequence([])

letter_list = ['j', 'n', 'd', 'f']

task = TimelineVariable('task', ['word_naming', 'color_naming'])
color = TimelineVariable('color', ['red', 'green', 'blue', 'yellow'])
response = TimelineVariable('response', ['red', 'green', 'blue', 'yellow'])


# cue, fixation, task, sci, feedback
# 400, 500, 2000,  400, im task kein feedback
def is_square(task):
    return task == "word_naming"


def is_triangle(task):
    return task == "color_naming"


square_shape = DerivedLevel('square', is_square, [task])
triangle_shape = DerivedLevel('triangle', is_triangle, [task])

cue_shape = DerivedParameter("shape", [square_shape, triangle_shape])

cue = SymbolStimulus(400, cue_shape)

fixation = FixationStimulus(500)


def is_correct_1(response):
    return response == 'red'


def is_correct_2(response):
    return response == 'green'


def is_correct_3(response):
    return response == 'yellow'


def is_correct_4(response):
    return response == 'blue'


letter_1 = DerivedLevel(letter_list[0], is_correct_1, [response])
letter_2 = DerivedLevel(letter_list[1], is_correct_2, [response])
letter_3 = DerivedLevel(letter_list[2], is_correct_3, [response])
letter_4 = DerivedLevel(letter_list[3], is_correct_4, [response])

correct_letter = DerivedParameter('correct', [letter_1, letter_2, letter_3, letter_4])

stroop = TextStimulus(2000, TimelineVariable('word'), color, ['j', 'n', 'd', 'f'], correct_letter)

blank = BlankStimulus(400)

train_block = TrialBlock([cue, fixation, stroop, blank])

experiment = Experiment([train_block])

##### HERE STOPS THE *** SWEETBEAN *** CODE

text = experiment.to_psych()

with open('test.js', 'w') as f:
    f.write(text)
