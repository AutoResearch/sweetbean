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
        "bandit_3": {"color": "red", "value": 5},
    },
    {
        "bandit_1": {"color": "orange", "value": 9},
        "bandit_2": {"color": "blue", "value": 1},
        "bandit_3": {"color": "red", "value": 5},
    },
    {
        "bandit_1": {"color": "orange", "value": 8},
        "bandit_2": {"color": "blue", "value": 2},
        "bandit_3": {"color": "red", "value": 5},
    },
    {
        "bandit_1": {"color": "orange", "value": 7},
        "bandit_2": {"color": "blue", "value": 3},
        "bandit_3": {"color": "red", "value": 5},
    },
    {
        "bandit_1": {"color": "orange", "value": 6},
        "bandit_2": {"color": "blue", "value": 4},
        "bandit_3": {"color": "red", "value": 5},
    },
]

bandit_1 = TimelineVariable("bandit_1")
bandit_2 = TimelineVariable("bandit_2")
bandit_3 = TimelineVariable("bandit_3")

score = SharedVariable("score", 0)
value = DataVariable("value", 0)

update_score = FunctionVariable(
    "update_score", lambda sc, val: sc + val, [score, value]
)

update_score_side_effect = SideEffect(score, update_score)

bandit_task = Bandit(
    bandits=[bandit_1, bandit_2, bandit_3],
    side_effects=[update_score_side_effect],
)
show_score = Text(duration=1000, text=score)

block = Block([bandit_task, show_score], timeline=timeline)

# Create an image of the stimuli sequence of the block
block.to_image("bandit.png", [{"value": 5}, None], zoom_factor=[1, 3])

# Create HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("bandit.html")
