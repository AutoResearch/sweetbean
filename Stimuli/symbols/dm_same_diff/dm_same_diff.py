from sweetbean import Block, Experiment
from sweetbean.stimulus import Symbol
from sweetbean.variable import FunctionVariable, TimelineVariable

timeline = [
    {"sample_color": "red", "probe_color": "red"},
    {"sample_color": "green", "probe_color": "red"},
]

sample = Symbol(
    shape="triangle",
    color=TimelineVariable("sample_color"),
    duration=500,
)

delay = Symbol(
    shape="cross",
    color="#888",
    duration=800,
)

probe = Symbol(
    shape="triangle",
    color=TimelineVariable("probe_color"),
    duration=1500,
    choices=["f", "j"],
    response_ends_trial=True,
    # F = same, J = different
    correct_key=FunctionVariable(
        "ck",
        lambda s, p: "f" if str(s).lower() == str(p).lower() else "j",
        [TimelineVariable("sample_color"), TimelineVariable("probe_color")],
    ),
)

block = Block([sample, delay, probe], timeline)
Experiment([block]).to_html("dms_same_diff.html")
