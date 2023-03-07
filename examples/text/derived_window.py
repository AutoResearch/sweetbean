from sweetbean.stimulus import TextStimulus
from sweetbean.parameter import TimelineVariable, DataVariable, DerivedLevel, DerivedParameter
from sweetbean.sequence import Block, Experiment

timeline = [
    {'color': 'red', 'word': 'RED', 'correct_key': 'f'},
    {'color': 'green', 'word': 'GREEN', 'correct_key': 'j'},
    {'color': 'green', 'word': 'RED', 'correct_key': 'f'},
    {'color': 'red', 'word': 'GREEN', 'correct_key': 'j'},
]

color = TimelineVariable('color', ['red', 'green'])
word = TimelineVariable('word', ['RED', 'GREEN'])
correct_key = TimelineVariable('correct_key', ['j', 'f'])

# Creating a data variable
correct = DataVariable("correct", [True, False])

# Predicates
def is_correct(correct):
    return correct
def is_false(correct):
    return not correct

# Derived Levels
correct_feedback = DerivedLevel("correct", is_correct, [correct], 2)
false_feedback = DerivedLevel("false", is_false, [correct], 2)

# Derived Parameter
feedback_text = DerivedParameter("feedback_text", [correct_feedback, false_feedback])

# Using it in the stimulus
feedback = TextStimulus(800, feedback_text)



fixation = TextStimulus(1000, '+')
so_s = TextStimulus(400)
stroop = TextStimulus(2000, word, color, ['j', 'f'], correct_key)
so_f = TextStimulus(300)
feedback = TextStimulus(800, feedback_text)

train_block = Block([fixation, so_s, stroop, so_f, feedback], timeline)
experiment = Experiment([train_block])

experiment.to_html('derived_window.html')
