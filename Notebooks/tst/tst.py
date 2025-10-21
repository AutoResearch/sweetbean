from sweetbean import Block, Experiment
from sweetbean.stimulus import Bandit, Text
from sweetbean.util.prompts import demographic
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

trial_sequence = Block([bandit_task, show_score], timeline=timeline)
experiment = Experiment([trial_sequence])


data, prompts = experiment.run_on_language(preamble=demographic(37, "man"))

print(data, prompts)
