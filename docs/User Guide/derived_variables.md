# Derived Variables

In the previous examples, we have seen how to create a simple block with a fixed trials. Here, we will introduce derived
variables. These variables allow us let a ``TimeLineVariable`` depend on another ``TimeLineVariable``. This can be useful when providing feedback as a function of the participant's response. 

Let us assume the same timeline:

```python

timeline = [
    {"color": "red", "word": "RED"},
    {"color": "green", "word": "GREEN"},
    {"color": "green", "word": "RED"},
    {"color": "red", "word": "GREEN"},
]
```

First, we create the timeline variables

```python
from sweetbean.parameter import TimelineVariable

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])
```

Now, we can create conditions (in form of functions). Here, we want to specify that the correct key is f if the color of
the Stroop Stimulus is red and j if it is green.

```python
def is_correct_f(color):
    return color == "red"


def is_correct_j(color):
    return not is_correct_f(color)
```

We can now create a derived level by specifying the value of the level, the condition and on what variable it is
depending on:

```python
from sweetbean.parameter import DerivedLevel

j_key = DerivedLevel("j", is_correct_j, [color])
f_key = DerivedLevel("f", is_correct_f, [color])
```

We can now create a derived parameter with the derived levels:

```python
from sweetbean.parameter import DerivedParameter

correct_key = DerivedParameter("correct", [j_key, f_key])
```

Now, we can use the derived Parameter in our stimuli:

```python
from sweetbean.stimulus import TextStimulus, FixationStimulus

fixation = FixationStimulus(1000)
stroop = TextStimulus(2000, word, color, ["j", "f"], correct_key)
```

Finally, we can create a block with the timeline. Here, we pass in the timeline to the block. The event sequence will
then be repeated as many times as there are entries in the timeline using the variables defined above.

```python

event_sequence = [fixation, stroop]

train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])

experiment.to_html("stroop.html")
```

There is one additional variable, that we can use: The data variable. It is a special variable that accesses data from previous stimuli to dynamically adjust the current stimulus. For example, we can create Feedback:
[Data Variables](data_variables.md)
