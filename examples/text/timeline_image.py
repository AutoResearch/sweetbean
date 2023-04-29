from sweetbean.parameter import TimelineVariable
from sweetbean.sequence import Block, sequence_to_image
from sweetbean.stimulus import BlankStimulus, TextStimulus

timeline = [
    {"color": "red", "word": '<div style="font-size: 110pt">RED</div>', "soa": 300},
    {"color": "green", "word": "GREEN", "soa": 200},
    {"color": "green", "word": "RED", "soa": 400},
    {"color": "red", "word": "GREEN", "soa": 500},
]

# ** declare the timeline variables ** #

# color: The name has to be color (it is the name in the timeline),
# and it has the levels red and green
color = TimelineVariable(name="color", levels=["red", "green"])

# word: The name has to be word (it is the name in the timeline),
# and it has the levels RED and GREEN
word = TimelineVariable(name="word", levels=["RED", "GREEN"])

# declare the timeline variable for soa
soa = TimelineVariable(name="soa", levels=[200, 300, 400, 500])

# ** declaring the different stimuli ** #

# fixation onset (a blank screen for 600ms)
fixation_onset = BlankStimulus(duration=600)

# fixation cross (the character "+" shown for 800ms)
fixation = TextStimulus(duration=800, text="<div style='font-size: 110pt'>+</div>")

# stimulus onset (a blank screen shown for 200ms)
stimulus_onset = BlankStimulus(duration=soa)

# the Stroop stimulus. Here instead of fixed parameters,
# we use the timeline variables, that we defined previously.
stroop = TextStimulus(duration=2500, text=word, color=color)

stroop_block = Block([fixation_onset, fixation], timeline)

sequence_to_image(stroop_block, durations=["600", "800"])
