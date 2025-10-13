from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import Text
from sweetbean.stimulus.Foraging import Foraging
from sweetbean.variable import TimelineVariable

# --- Timeline with per-trial item arrays (targets/distractors) ---
# Each item can define ONE of: html | text | shape | src
# Optional: color, rotationDeg, pos, size, fontSize, id, attrs
timeline = [
    {
        "targets": [
            {"text": "O", "color": "blue"},
            {"text": "O", "color": "blue"},
        ],
        "distractors": [
            {"text": "O", "color": "red"},
            {"text": "Q", "color": "blue"},
            {"text": "Q", "color": "red"},
        ],
        # blue Os
    },
    {
        "targets": [
            {"shape": "square", "color": "red"},
            {"shape": "square", "color": "blue"},
        ],
        "distractors": [
            {"shape": "triangle", "color": "red"},
            {"shape": "circle", "color": "blue"},
            {"shape": "triangle", "color": "blue"},
        ],
        # squares
    },
    {
        "targets": [
            {"html": "<b>?</b>", "color": "red"},
            {"html": "<b>!</b>", "color": "blue"},
        ],
        "distractors": [
            {"html": "?", "color": "red"},
            {"html": "!", "color": "blue"},
            {"html": "!", "color": "blue"},
        ],
        # bold punctuation
    },
    {
        "targets": [
            {"src": "https://dummyimage.com/256x256/ffffff/000000&text=T1"},
            {"src": "https://dummyimage.com/256x256/ffffff/000000&text=T2"},
        ],
        "distractors": [
            {"src": "https://dummyimage.com/256x256/ffffff/000000&text=D1"},
            {"src": "https://dummyimage.com/256x256/ffffff/000000&text=D2"},
            {"src": "https://dummyimage.com/256x256/ffffff/000000&text=D3"},
        ],
        # Ts
    },
]

# Instruction screen before each foraging trial (like your Text “response window” in RSVP)
instructions = Text(
    text="Collect ALL targets as fast as you can. "
    "Distractors will jiggle. Tap/click targets to collect.",
    duration=1500,  # auto-advance after 1.5s
)

# Foraging stimulus:
# - Defaults: random non-overlapping placement inside a centered arena,
#   black bg, end_when_found=True, trial_duration=None.
foraging = Foraging(
    targets=TimelineVariable("targets"),
    distractors=TimelineVariable("distractors"),
)

# Put them together
stimulus_sequence = [instructions, foraging]

block = Block(stimulus_sequence, timeline=timeline)
exp = Experiment([block])

# Will use your HTML preamble (already loading @sweet-jspsych/plugin-foraging)
exp.to_html("foraging.html")
