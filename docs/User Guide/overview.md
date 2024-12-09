# Overview

## Installation

SweetBean can be installed via pip:

```bash
pip install sweetbean
```

## Usage

### A single Introduction Trial

To create a SweetBean experiment, you define a sequence of stimuli.
For example, the following code defines a simple text stimulus to welcome participants. `:

```python
from sweetbean.stimulus import Text

welcome = Text("Welcome to the experiment! Press >>Space<< to begin", choices=[" "])
```

We then use stimuli to create a sequence of events:

```python
event_sequence = [welcome]
```

From sequences, we can create a block:

```python
from sweetbean import Block

introduction_block = Block(event_sequence)
```

Finally, we can create the experiment...

```python
from sweetbean import Experiment

experiment = Experiment([indroduction_block])
```

... and export the experiment as html file

```python
experiment.to_html("basic.html")
```

### Multiple Trials

Let us create a stroop experiment. The trials should start with a fixation cross, followed by a colored word:

```python
from sweetbean.stimulus import Text, Fixation

fixation_1 = Fixation(duration=500)
stroop_1 = Text("RED", color="red", choices=["r", "g"])
fixation_2 = Fixation(duration=500)
stroop_2 = Text("GREEN", color="green", choices=["r", "g"])
fixation_3 = Fixation(duration=500)
...
```

We can then create a sequence of events and blocks as before.

```python
event_sequence_stroop = [fixation_1, stroop_1, fixation_2, stroop_2, fixation_3, ...]
stroop_block = Block(event_sequence_stroop)
experiment = Experiment([introduction_block, stroop_block])
experiment.to_html("stroop.html")
```

This way, we could use loops to create experiments with many trials. But a better way is to use
the `timeline variables`: [Timeline Variables](./timeline_variables.md)
