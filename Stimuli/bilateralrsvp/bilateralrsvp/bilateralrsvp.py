from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import BilateralRSVP, Feedback, Text
from sweetbean.variable import FunctionVariable, TimelineVariable

# -------------------------
# Trial table (streams are PURE CONTENT)
# -------------------------
timeline = [
    {
        "left_stream": ["O", "O", "Q", "Q", "O", "Q"],
        "right_stream": ["1", "1", "2", "3", "4", "5"],
        "left_target_index": 4,  # zero-based
        "left_target_shape": "circle",
        "right_target_index": 4,
        "right_target_shape": "square",
        "correct_key": "o",
    },
    {
        "left_stream": ["O", "Q", "Q", "O", "Q", "O"],
        "right_stream": ["1", "1", "2", "3", "4", "5"],
        "left_target_index": 2,
        "left_target_shape": "circle",
        "right_target_index": 2,
        "right_target_shape": "square",
        "correct_key": "q",
    },
    {
        "left_stream": ["O", "O", "Q", "O", "O", "O"],
        "right_stream": ["1", "1", "2", "3", "4", "5"],
        "left_target_index": 2,
        "left_target_shape": "square",
        "right_target_index": 2,
        "right_target_shape": "circle",
        "correct_key": "2",
    },
]


# -------------------------
# Helper functions for per-trial logic
# -------------------------
def pick_target_side(left_shape, right_shape):
    ls = str(left_shape).strip().lower()
    rs = str(right_shape).strip().lower()
    if ls == "circle" and rs != "circle":
        return "left"
    if rs == "circle" and ls != "circle":
        return "right"
    return "left"


def pick_target_index(side, left_idx, right_idx):
    return int(left_idx) if str(side) == "left" else int(right_idx)


def pick_target_shape(side, left_shape, right_shape):
    return (
        (str(left_shape) if str(side) == "left" else str(right_shape)).strip().lower()
    )


def pick_distractor_shape(side, left_shape, right_shape):
    # use the *other* side's shape as the distractor decoration
    return (
        (str(right_shape) if str(side) == "left" else str(left_shape)).strip().lower()
    )


def plus_one(i):  # for post-target distractor at t+1
    return int(i) + 1


# -------------------------
# Variables (evaluated per timeline row)
# -------------------------
var_target_side = FunctionVariable(
    name="target_side",
    fct=pick_target_side,
    args=[
        TimelineVariable("left_target_shape"),
        TimelineVariable("right_target_shape"),
    ],
)

var_target_index = FunctionVariable(
    name="target_index",
    fct=pick_target_index,
    args=[
        var_target_side,
        TimelineVariable("left_target_index"),
        TimelineVariable("right_target_index"),
    ],
)

var_target_shape = FunctionVariable(
    name="target_shape",
    fct=pick_target_shape,
    args=[
        var_target_side,
        TimelineVariable("left_target_shape"),
        TimelineVariable("right_target_shape"),
    ],
)

var_distractor_shape = FunctionVariable(
    name="distractor_shape",
    fct=pick_distractor_shape,
    args=[
        var_target_side,
        TimelineVariable("left_target_shape"),
        TimelineVariable("right_target_shape"),
    ],
)

var_post_index = FunctionVariable(
    name="post_index",
    fct=plus_one,
    args=[var_target_index],
)


# -------------------------
# Shared response + feedback
# -------------------------
def make_response_window(prompt="What was the target symbol?"):
    return Text(
        text=prompt,
        choices=list("abcdefghijklmnopqrstuvwxyz0123456789"),
        correct_key=TimelineVariable("correct_key"),
    )


def make_feedback():
    return Feedback(duration=300)


# -------------------------
# VARIANT 1 — Color-only targets (shape 'none') + underline distractor (opposite side)
# -------------------------
rsvp_v1 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape="none",
    target_color="#00b050",  # colors the glyph itself
    distractor_shape="underline",
    distractor_color="#888",
    stimulus_duration=200,
    isi=40,
    choices="NO_KEYS",
)
block_v1 = Block([rsvp_v1, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# VARIANT 2 — Target HTML template + circle distractor
# -------------------------
rsvp_v2 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape="none",  # HTML wrapper handles appearance
    target_html=(
        '<span style="font-weight:800;color:#ff4d4d;'
        'border-bottom:3px solid #ff7f00;padding:0.05em 0.2em">{{content}}</span>'
    ),
    distractor_shape="circle",
    distractor_color="#bbbbbb",
    stimulus_duration=200,
    isi=40,
    choices="NO_KEYS",
)
block_v2 = Block([rsvp_v2, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# VARIANT 3 — Arrays/broadcasting (two targets + two distractors)
# NOTE: This is a multi-target demo; your response window still asks for a single key.
# -------------------------
rsvp_v3 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    # two targets
    target_index=[2, 4],
    target_side=["left", "right"],
    target_shape=["circle", "square"],
    target_color=["#00b050", "#ff7f00"],
    # two distractors (sides omitted → opposite of each target)
    distractor_index=[2, 4],
    distractor_shape=["underline", "circle"],
    distractor_color=["#888", "#bbb"],
    stimulus_duration=180,
    isi=40,
    choices="NO_KEYS",
)
block_v3 = Block(
    [
        rsvp_v3,
        make_response_window("(Demo) Enter any target you saw:"),
        make_feedback(),
    ],
    timeline=timeline,
)

# -------------------------
# VARIANT 4 — Post-target distractor at index + 1 (opposite side by default)
# -------------------------
rsvp_v4 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape="none",
    target_color="#167ad3",
    distractor_index=var_post_index,  # t+1
    distractor_shape="underline",
    distractor_color="#888",
    stimulus_duration=50,  # EEG-style 50/50 → 10 Hz
    isi=50,
    choices="NO_KEYS",
)
block_v4 = Block([rsvp_v4, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# VARIANT 5 — Mask between frames (ISI) + classic circle target
# (Kept NO_KEYS so response is collected afterward for consistency.)
# -------------------------
rsvp_v5 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape="circle",
    target_color="#30c050",
    distractor_shape="none",
    stimulus_duration=120,
    isi=40,
    mask_html="•",  # shown during ISI
    choices="NO_KEYS",
)
block_v5 = Block([rsvp_v5, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# VARIANT 6 — Per-item HTML on distractor (highlight box), color-only target
# -------------------------
rsvp_v6 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape="none",
    target_color="#ff8c00",
    distractor_shape="none",
    distractor_html=(
        '<span style="display:inline-block;padding:0.1em 0.25em;'
        'border:2px solid #aaa;border-radius:8%">{{content}}</span>'
    ),
    stimulus_duration=200,
    isi=40,
    choices="NO_KEYS",
)
block_v6 = Block([rsvp_v6, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# VARIANT 7 — Fix distractor side to LEFT (override opposite-side default)
# -------------------------
rsvp_v7 = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape=var_target_shape,  # per-trial circle/square from table
    distractor_side="left",  # force left regardless of target_side
    distractor_index=var_target_index,
    distractor_shape="square",
    distractor_color="#999",
    stimulus_duration=200,
    isi=40,
    choices="NO_KEYS",
)
block_v7 = Block([rsvp_v7, make_response_window(), make_feedback()], timeline=timeline)

# -------------------------
# Build and export one experiment
# -------------------------
intro = Text(
    text="Bilateral RSVP - multiple variants. Press any key to begin.", choices="ALL"
)
outro = Text(text="Done. Thanks!", choices="ALL")

exp = Experiment(
    [
        Block([intro]),
        block_v1,
        block_v2,
        block_v3,
        block_v4,
        block_v5,
        block_v6,
        block_v7,
        Block([outro]),
    ]
)

exp.to_html("bilateralrsvp.html")
