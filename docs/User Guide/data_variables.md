# Data Variables

In the previous example, we created a derived parameter that determined the correct key based on the color of the Stroop
stimulus. We can now create a data variable that determines whether the participant pressed the correct key. We can then
use this data variable to create feedback for the participant.

Assume the same timeline as before and the same derived parameter:

```python
from sweetbean.variable import (
    DataVariable,
    FunctionVariable,
    TimelineVariable,
)
from sweetbean import Block, Experiment
from sweetbean.stimulus import Text

timeline = [
    {"color": "red", "word": "RED"},
    {"color": "green", "word": "GREEN"},
    {"color": "green", "word": "RED"},
    {"color": "red", "word": "GREEN"},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])


def correct_key_fct(col):
    if col == "red":
        return "f"
    elif col == "green":
        return "j"


correct_key = FunctionVariable("correct", correct_key_fct, [color])
```

Now we can create a `DataVariable` that determines whether the participant pressed the correct key. The `1` in the
declaration indicates from which stimulus to get the variable (1 = previous, 2 = second previous, etc.).
We can use the `DataVariable` directly as parameter in stimuli, or we can us it as input for a `FunctionVariable` to create the feedback text:

```python
correct = DataVariable("correct", 1)

# Predicates
def feedback_text_fct(was_correct):
    if was_correct:
        return "That was correct!"
    else:
        return "That was false!"


feedback_text = feedback_text_fct("feedback_text", feedback_txt_fct, [correct])
```

Again, we can use this in a feedback stimulus.

```python

fixation = FixationStimulus(500)
stroop = TextStimulus(2000, word, color, ["j", "f"], correct_key)
feedback = TextStimulus(800, feedback_text)

event_sequence = [fixation, stroop, feedback]


train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])

experiment.to_html("stroop.html")
```

There is one additional variable type, that we can use: The shared variable. It is a special variable that can be shared across different trials and can be updated via side effects:
[Shared Variables And Side Effects](data_variables.md)
