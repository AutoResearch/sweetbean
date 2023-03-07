from sweetbean.stimulus import TextStimulus
from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, Experiment

timeline = [
    {'color': 'red', 'word': 'RED', 'so_s': 200, 'so_f': 1000, 'correct_key': 'f'},
    {'color': 'green', 'word': 'GREEN', 'so_s': 1000, 'so_f': 100, 'correct_key': 'j'},
    {'color': 'green', 'word': 'RED', 'so_s': 100, 'so_f': 2000, 'correct_key': 'f'},
    {'color': 'red', 'word': 'GREEN', 'so_s': 1000, 'so_f': 1000, 'correct_key': 'j'},
]

color = TimelineVariable('color', ['red', 'green'])
word = TimelineVariable('word', ['RED', 'GREEN'])
so_s_duration = TimelineVariable('so_s', [100, 200, 1000])
so_f_duration = TimelineVariable('so_f', [100, 1000, 2000])
correct_key = TimelineVariable('correct_key', ['j', 'f'])

fixation = TextStimulus(800, '+')
so_s = TextStimulus(so_s_duration)
stroop = TextStimulus(2000, word, color, ['f', 'j'], correct_key)
so_f = TextStimulus(so_f_duration)

train_block = Block([fixation, so_s, stroop, so_f], timeline)
experiment = Experiment([train_block])


experiment.to_html('timeline.html')