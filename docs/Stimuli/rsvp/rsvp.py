from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus.RSVP import RSVP

trial = RSVP(
    streams=[
        {"id": "left", "items": ["O", "O", "Q", "O", "O", "O"]},
        {"id": "right", "items": ["O", "O", "O", "O", "Q", "O"]},
    ],
    stimulus_duration=200,
    isi=40,
    targets=[
        {"stream_id": "left", "index": 2, "correct_keys": ["f"], "shape": "circle"},
        {"stream_id": "right", "index": 4, "correct_keys": ["j"], "shape": "square"},
    ],
)

block = Block([trial])
exp = Experiment([block])
exp.to_html("rsvp.html")
