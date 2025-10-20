from sweetbean import Block, Experiment
from sweetbean.stimulus import Symbol
from sweetbean.variable import FunctionVariable, TimelineVariable

# constants
PPD = 60
X_LEFT = int(round(-6 * PPD))  # -360 px
X_RIGHT = int(round(6 * PPD))  # 360 px
R_CUE = int(round(0.4 * PPD))  # 24 px
R_TGT = int(round(0.35 * PPD))  # 21 px

timeline = [
    {"cue_side": "left", "target_side": "left"},  # valid
    {"cue_side": "right", "target_side": "left"},  # invalid
]

fix = Symbol(shape="cross", color="#4d4d4d", duration=300)

cue = Symbol(
    items=[
        {"shape": "circle", "x": X_LEFT, "y": 0, "color": "#666"},
        {"shape": "circle", "x": X_RIGHT, "y": 0, "color": "#666"},
        {
            "shape": "circle",
            "x": FunctionVariable(
                "x",
                lambda side, L, R: L if side == "left" else R,
                [TimelineVariable("cue_side"), X_LEFT, X_RIGHT],
            ),
            "y": 0,
            "color": "#fff",
            "radius": R_CUE,
        },
    ],
    duration=100,
)

isi = Symbol(shape="cross", color="#4d4d4d", duration=200)

target = Symbol(
    items=[
        {"shape": "circle", "x": X_LEFT, "y": 0, "color": "#fff", "radius": R_TGT},
        {"shape": "circle", "x": X_RIGHT, "y": 0, "color": "#fff", "radius": R_TGT},
        {
            # mask the non-target by making it gray
            "shape": "circle",
            "x": FunctionVariable(
                "x",
                lambda side, L, R: R
                if side == "left"
                else L,  # opposite of target side
                [TimelineVariable("target_side"), X_LEFT, X_RIGHT],
            ),
            "y": 0,
            "color": "#808080",
            "radius": R_TGT,
        },
    ],
    duration=1200,
    choices=["f", "j"],
    response_ends_trial=True,
    # F = left, J = right
    correct_key=FunctionVariable(
        "ck",
        lambda side: "f" if side == "left" else "j",
        [TimelineVariable("target_side")],
    ),
)

block = Block([fix, cue, isi, target], timeline)
Experiment([block]).to_html("posner.html")
