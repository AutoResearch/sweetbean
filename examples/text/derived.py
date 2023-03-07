from sweetbean.stimulus import TextStimulus
from sweetbean.parameter import TimelineVariable, DerivedLevel, DerivedParameter
from sweetbean.sequence import Block, Experiment

timeline = [
    {'color': 'red', 'word': 'RED', 'task': 'color_naming'},
    {'color': 'green', 'word': 'GREEN', 'task': 'color_naming'},
    {'color': 'green', 'word': 'RED', 'task': 'word_reading'},
    {'color': 'red', 'word': 'GREEN', 'task': 'word_reading'},
]

color = TimelineVariable('color', ['red', 'green'])
word = TimelineVariable('word', ['RED', 'GREEN'])
task = TimelineVariable('task', ['color_naming', 'word_reading'])


def is_fixation_x(task):
    return task == 'word_reading'


def is_fixation_plus(task):
    return task == 'color_naming'


x_shape = DerivedLevel('x', is_fixation_x, [task])
plus_shape = DerivedLevel('+', is_fixation_plus, [task])

fixation_shape = DerivedParameter('fixation_shape', [x_shape, plus_shape])


def is_correct_f(word, color, task):
    return (task == 'word_reading' and word == 'RED') or \
        (task == 'color_naming' and color == 'red')


def is_correct_j(word, color, task):
    return not is_correct_f(word, color, task)


j_key = DerivedLevel('j', is_correct_j, [word, color, task])
f_key = DerivedLevel('f', is_correct_f, [word, color, task])

correct_key = DerivedParameter('correct', [j_key, f_key])

fixation = TextStimulus(1000, fixation_shape)
so_s = TextStimulus(800)
stroop = TextStimulus(2000, word, color, ['j', 'g'], correct_key)
so_f = TextStimulus(300)

train_block = Block([fixation, so_s, stroop, so_f], timeline)
experiment = Experiment([train_block])

experiment.to_html('derived.html')