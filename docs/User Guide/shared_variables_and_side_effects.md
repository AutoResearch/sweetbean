# Shared Variables And Side Effects

Shared Variables are variables that can be shared across different trials. They can be updated via Side Effects. This can be useful, for example, when we want to keep track of the participant's score.

Assume, we have a two-armed bandit task and want to present the score of the participant after each choice.

As in the previous examples, we first define the timeline and the timeline variables:
```python
from sweetbean import Block, Experiment
from sweetbean.stimulus import Bandit, Text
from sweetbean.variable import (
    DataVariable,
    FunctionVariable,
    SharedVariable,
    SideEffect,
    TimelineVariable,
)

timeline = [
    {
        "bandit_1": {"color": "orange", "value": 10},
        "bandit_2": {"color": "blue", "value": 0},
    },
    {
        "bandit_1": {"color": "orange", "value": 9},
        "bandit_2": {"color": "blue", "value": 1},
    },
    {
        "bandit_1": {"color": "orange", "value": 8},
        "bandit_2": {"color": "blue", "value": 2},
    },
    {
        "bandit_1": {"color": "orange", "value": 7},
        "bandit_2": {"color": "blue", "value": 3},
    },
    {
        "bandit_1": {"color": "orange", "value": 6},
        "bandit_2": {"color": "blue", "value": 4},
    },
]

bandit_1 = TimelineVariable("bandit_1")
bandit_2 = TimelineVariable("bandit_2")
```

Next, we define the shared variable `score`. The start value will be 0, and we will update it with the `update_score` function by adding the `value` of the chosen bandit to the score. Since we need the `value` of the chosen bandit, we also define a data variable that gets the value with the window 0 (current trial).

```python

score = SharedVariable("score", 0)
value = DataVariable("value", 0)

updated_score = FunctionVariable(
    "updated_score", lambda sc, val: sc + val, [score, value]
)
```

We can now create a side effect that updates the score with the `update_score` function. We pass the score and the function to the side effect. A side effects takes in the variable to set (in this case the score) and the variable it will be set to (in this case the function variable `update_score`).

We can pass in as many side effects as we want to a stimulus as a list of side effects. Here, we only have one side effect that updates the score.

```python
update_score_side_effect = SideEffect(score, updated_score)

bandit_task = Bandit(
    bandits=[bandit_1, bandit_2, bandit_3],
    side_effects=[update_score_side_effect],
)
```

Finally, we can show the score after each choice with a text stimulus. We pass the score to the text stimulus.

```python
show_score = Text(duration=1000, text=score)
```

Then we create the experiment as before and export it as a html file.

```python

trial_sequence = Block([bandit_task, show_score], timeline=timeline)
experiment = Experiment([trial_sequence])
experiment.to_html("bandit.html")
```