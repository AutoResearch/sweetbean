from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import BilateralRSVP, Feedback, Text
from sweetbean.variable import FunctionVariable, TimelineVariable

timeline = [
    {
        "left_stream": ["O", "O", "Q", "Q", "O", "Q"],
        "right_stream": ["1", "1", "2", "3", "4", "5"],
        "left_target_index": 4,  # zero-based index
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


# --- mapping helpers (as FunctionVariables) ---
def pick_target_side(left_shape, right_shape):
    ls = str(left_shape).strip().lower()
    rs = str(right_shape).strip().lower()
    if ls == "circle" and rs != "circle":
        return "left"
    if rs == "circle" and ls != "circle":
        return "right"
    # fallback
    return "left"


def pick_target_index(side, left_idx, right_idx):
    return int(left_idx) if str(side) == "left" else int(right_idx)


def pick_target_shape(side, left_shape, right_shape):
    return (
        (str(left_shape) if str(side) == "left" else str(right_shape)).strip().lower()
    )


def pick_distractor_shape(side, left_shape, right_shape):
    # use the other side's shape as the distractor decoration
    return (
        (str(right_shape) if str(side) == "left" else str(left_shape)).strip().lower()
    )


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

# NOTE: We do not set distractor_index; your js plugin defaults it to target_index.
var_distractor_shape = FunctionVariable(
    name="distractor_shape",
    fct=pick_distractor_shape,
    args=[
        var_target_side,
        TimelineVariable("left_target_shape"),
        TimelineVariable("right_target_shape"),
    ],
)

# --- stimuli ---
rsvp = BilateralRSVP(
    left=TimelineVariable("left_stream"),
    right=TimelineVariable("right_stream"),
    target_side=var_target_side,
    target_index=var_target_index,
    target_shape=var_target_shape,
    # opposite-stream distractor, same index as target by default:
    distractor_shape=var_distractor_shape,
    # Timing
    stimulus_duration=200,
    isi=40,
    # We want responses after the RSVP, so ignore keys during RSVP:
    choices="NO_KEYS",
)

response_window = Text(
    text="What was the circled symbol?",
    choices=[
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
    ],
    correct_key=TimelineVariable("correct_key"),
)

feedback = Feedback(duration=300)

block = Block([rsvp, response_window, feedback], timeline=timeline)
exp = Experiment([block])
exp.to_html("bilateralrsvp.html")
