from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import RSVP, Feedback, Text
from sweetbean.variable import TimelineVariable

# Trial table (streams are pure content)
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

rsvp = RSVP(
    # Streams are pure content (no "circle"/"square"/color tokens here)
    streams=[
        {"id": "left", "items": TimelineVariable("left_stream")},
        {"id": "right", "items": TimelineVariable("right_stream")},
    ],
    stimulus_duration=200,
    isi=40,
    # Disable responses during the RSVP; we ask afterward on a blank screen
    choices="NO_KEYS",
    # Convenience arrays — plugin broadcasts & renders per item
    target_index=[
        TimelineVariable("left_target_index"),
        TimelineVariable("right_target_index"),
    ],
    target_side=["left", "right"],
    target_shape=[
        TimelineVariable("left_target_shape"),
        TimelineVariable("right_target_shape"),
    ],
    # (optional) default outline thickness for targets
    target_stroke="3px",
    # No explicit `targets=[...]` needed now; the three arrays above define them
)

response_window = Text(
    text="What was the target symbol?",
    choices=list("abcdefghijklmnopqrstuvwxyz0123456789"),
    correct_key=TimelineVariable("correct_key"),
)

feedback = Feedback(duration=300)

block = Block([rsvp, response_window, feedback], timeline=timeline)
exp = Experiment([block])
exp.to_html("rsvp.html")
