from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import BilateralRSVP

# -------------------------
# VARIANT 7 — Fix distractor side to LEFT (override opposite-side default)
# -------------------------
bi_rsvp = BilateralRSVP(
    left=["a", "b", "c"],
    right=[1, 2, 3],
    target_side="left",
    target_index=2,
    target_shape="circle",  # per-trial circle/square from table
    distractor_shape="square",
    distractor_index=2,
    stimulus_duration=200,
    isi=40,
    choices="NO_KEYS",
)
block = Block([bi_rsvp])


exp = Experiment(
    [
        block,
    ]
)

exp.to_html("bilateralrsvp_simple.html")
