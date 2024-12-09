# Timeline Variables

In the previous examples, we have seen how to create a simple block with a fixed trials. Here, we will introduce
timeline variables that can be used to create more complex experiments with multiple trials.

Consider the following timeline that consists of words and colors for a Stroop Task:

```python
timeline = [
    {"color": "red", "word": 'RED'},
    {"color": "green", "word": "GREEN"},
    {"color": "green", "word": "RED"},
    {"color": "red", "word": "GREEN"},
]
```

First, we declare SweetBean Timeline Variables:

color: The name has to be color (it has to match the key in the timeline)
word: The name has to be word (it has to match the key in the timeline)

```python
from sweetbean.variable import TimelineVariable

color = TimelineVariable(name="color")
word = TimelineVariable(name="word")


```

Now, we can use these timeline variables when defining the stimuli:

```python
from sweetbean.stimulus import Text, Fixation

fixation = FixationStimulus(duration=500)
stroop = TextStimulus(duration=1000, text=word, color=color)
```

Finally, we can create a block with the timeline. Here, we pass in the timeline to the block. The event sequence will
then be repeated as many times as there are entries in the timeline using the variables defined above.

```python
from sweetbean import Block, Experiment

event_sequence = [fixation, stroop]
stroop_block = Block(event_sequence, timeline)
experiment = Experiment(stroop_block)
experiment.to_html("stroop.html")

```

Additionally, to timeline variables, we can also create function variables. For example, we can create a variable that gives us the correct key press depending on the word of a StroopStimulus:
[Derived Variable](./function_variables.md)