from sweetbean_v2 import Block, Experiment
from sweetbean_v2.datatype.variables import (
    DataVariable,
    FunctionVariable,
    SharedVariable,
    SideEffect,
    TimelineVariable,
)
from sweetbean_v2.stimulus import Bandit, Text

timeline = [
    {
        "bandit_1": {"color": "orange", "value": 10},
        "bandit_2": {"color": "blue", "value": 0},
        "bandit_3": {"color": "red", "value": 5},
        "ta": 0,
    },
    {
        "bandit_1": {"color": "orange", "value": 5},
        "bandit_2": {"color": "blue", "value": 0},
        "bandit_3": {"color": "red", "value": 10},
        "ta": 0,
    },
]

bandit_1 = TimelineVariable("bandit_1")
bandit_2 = TimelineVariable("bandit_2")
bandit_3 = TimelineVariable("bandit_3")
ta = TimelineVariable("ta")

score = SharedVariable("score", 0)

value = DataVariable("value", 0)

update_score = FunctionVariable(
    "update_score", lambda score, value: score + value, [score, value]
)

se = SideEffect(score, update_score)


bandit_task = Bandit(
    bandits=[bandit_1, bandit_2, bandit_3],
    time_after_response=ta,
    side_effects=[se],
)
show_score = Text(duration=1000, text=score)

trial_sequence = Block([bandit_task, show_score], timeline=timeline)
experiment = Experiment([trial_sequence])
experiment.to_html("basic.html")
