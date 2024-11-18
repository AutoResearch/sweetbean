# Data Variables

In the previous example, we created a derived parameter that determined the correct key based on the color of the Stroop
stimulus. We can now create a data variable that determines whether the participant pressed the correct key. We can then
use this data variable to create feedback for the participant.

Assume the same timeline as before and the same derived parameter:

```python
from sweetbean.parameter import (
    DataVariable,
    DerivedLevel,
    DerivedParameter,
    TimelineVariable,
)
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus

timeline = [
    {"color": "red", "word": "RED"},
    {"color": "green", "word": "GREEN"},
    {"color": "green", "word": "RED"},
    {"color": "red", "word": "GREEN"},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])


def is_correct_f(color):
    return color == "red"


def is_correct_j(color):
    return not is_correct_f(color)


j_key = DerivedLevel("j", is_correct_j, [color])
f_key = DerivedLevel("f", is_correct_f, [color])

correct_key = DerivedParameter("correct", [j_key, f_key])
```

Now we can create a `DataVariable` that determines whether the participant pressed the correct key. The `1` in the
declaration indicates from which stimulus to get the variable (1 = previous, 2 = second previous, etc.).

```python
correct = DataVariable("correct", [True, False])

# Predicates
def is_correct(correct):
    return correct


def is_false(correct):
    return not correct


correct_feedback = DerivedLevel("correct", is_correct, [correct], 1)
false_feedback = DerivedLevel("false", is_false, [correct], 1)
```

Again, we can use the Derived Levels to create a Derived Parameter and use it in a feedback stimulus.

```python
feedback_text = DerivedParameter("feedback_text", [correct_feedback, false_feedback])

fixation = FixationStimulus(500)
stroop = TextStimulus(2000, word, color, ["j", "f"], correct_key)
feedback = TextStimulus(800, feedback_text)

event_sequence = [fixation, stroop, feedback]


train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])

experiment.to_html("stroop.html")
```
