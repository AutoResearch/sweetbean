from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import RSVP, Feedback, Text
from sweetbean.variable import TimelineVariable

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

rsvp = RSVP(
    streams=[
        {"id": "left", "items": TimelineVariable("left_stream")},
        {"id": "right", "items": TimelineVariable("right_stream")},
    ],
    stimulus_duration=200,
    isi=40,
    # IMPORTANT: disable responses during RSVP since you ask afterward
    choices="NO_KEYS",
    # (explicit for clarity; your plugin defaults to True)
    decorate_targets=True,
    targets=[
        {
            "stream_id": "left",
            "index": TimelineVariable("left_target_index"),
            "shape": TimelineVariable("left_target_shape"),
        },
        {
            "stream_id": "right",
            "index": TimelineVariable("right_target_index"),
            "shape": TimelineVariable("right_target_shape"),
        },
    ],
)

response_window = Text(
    text="What was the circled symbol?",
    choices=list("abcdefghijklmnopqrstuvwxyz0123456789"),
    correct_key=TimelineVariable("correct_key"),
)

feedback = Feedback(duration=300)

block = Block([rsvp, response_window, feedback], timeline=timeline)
exp = Experiment([block])
exp.to_html("rsvp.html")
