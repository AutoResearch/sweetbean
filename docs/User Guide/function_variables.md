# Function Variables

In the previous examples, we have seen how to create a simple block with a fixed trials. Here, we will introduce function
variables. These variables allow us let a ``FunctionVariable`` depend on other ``Variables``. This can be useful, for example, when providing feedback as a function of the participant's response. 

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
from sweetbean.variable import TimelineVariable

color = TimelineVariable("color")
word = TimelineVariable("word")
```

Now, we can create conditions (in form of functions). Here, we want to specify that the correct key is f if the color of
the Stroop Stimulus is red and j if it is green.

```python
def correct_key_fct(col):
    if col == "red":
        return "f"
    elif col == "green":
        return "j"
```

We can now create a function variable by specifying the name, the function, and which arguments to use (in this case the color)

```python
from sweetbean.variable import FunctionVariable

correct_key = FunctionVariable("correct", correct_key_fct, [color])
```

Now, we can use the function variable in our stimuli:

```python
from sweetbean.stimulus import Text, Fixation

fixation = Fixation(1000)
stroop = Text(2000, word, color, ["j", "f"], correct_key)
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
