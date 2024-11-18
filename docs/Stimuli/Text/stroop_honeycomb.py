from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, Experiment, Timeline
from sweetbean.stimulus import TextStimulus

t_0 = Timeline("t_0", "../assets/timelines/${global.ATTEMPTS}/0.json")
t_1 = Timeline("t_1", "../assets/timelines/${global.ATTEMPTS}/1.json")
t_2 = Timeline("t_2", "../assets/timelines/${global.ATTEMPTS}/2.json")

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])

text = TextStimulus(duration=2000, text=word, color=color, choices=["a", "b"])

block_0 = Block([text], t_0)
block_1 = Block([text], t_1)
block_2 = Block([text], t_2)
experiment = Experiment([block_0, block_1, block_2])

experiment.to_honeycomb(path_main="main.js")
