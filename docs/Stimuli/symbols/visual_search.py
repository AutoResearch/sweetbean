from sweetbean import Block, Experiment
from sweetbean.stimulus import Symbol
from sweetbean.variable import TimelineVariable

timeline = [
    {
        "items": [
            {"shape": "circle", "x": -300, "y": 0, "color": "#666"},
            {"shape": "circle", "x": 0, "y": 0, "color": "#666"},
            {"shape": "triangle", "x": 300, "y": 0, "color": "red"},  # target
        ],
        "correct_key": "f",  # F = present, J = absent
    },
    {
        "items": [
            {"shape": "circle", "x": -300, "y": 0, "color": "#666"},
            {"shape": "circle", "x": 0, "y": 0, "color": "#666"},
            {"shape": "circle", "x": 300, "y": 0, "color": "#666"},
        ],
        "correct_key": "j",
    },
]

fix = Symbol(shape="cross", color="#4d4d4d", duration=400)

search = Symbol(
    items=TimelineVariable("items"),
    duration=2000,
    choices=["f", "j"],
    correct_key=TimelineVariable("correct_key"),
)

block = Block([fix, search], timeline)

Experiment([block]).to_html("visual_search.html")
