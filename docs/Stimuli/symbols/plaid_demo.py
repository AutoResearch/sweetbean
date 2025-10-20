from sweetbean import Block, Experiment
from sweetbean.stimulus import Feedback, Symbol, Text
from sweetbean.variable import FunctionVariable, TimelineVariable

# --- constants / helpers ---
R_INNER = 100
R_OUTER = 180
BAR_PX = 12
GRAY55 = "#8c8c8c"

# Plaid contrast via two-tone palettes
STRONG_COLORS = ["#bbbbbb", "#333333"]
WEAK_COLORS = ["#999999", "#666666"]

timeline_left_right = [
    {
        "prime_deg": 0,
        "plaid_weak_deg": 135,
        "plaid_strong_deg": 45,
    },  # vertical prime, left-leaning weak, right-leaning strong
    {
        "prime_deg": 90,
        "plaid_weak_deg": 45,
        "plaid_strong_deg": 135,
    },  # horizontal prime, right-leaning weak, left-leaning strong
    {"prime_deg": 45, "plaid_weak_deg": 180, "plaid_strong_deg": 45},
    {"prime_deg": 135, "plaid_weak_deg": 90, "plaid_strong_deg": 135},
]

timeline_same_diff = [
    {"prime_deg": 0, "plaid_weak_deg": 135, "plaid_strong_deg": 45, "probe_ori": 45},
    {"prime_deg": 90, "plaid_weak_deg": 45, "plaid_strong_deg": 135, "probe_ori": 45},
    {"prime_deg": 45, "plaid_weak_deg": 180, "plaid_strong_deg": 90, "probe_ori": 0},
    {"prime_deg": 135, "plaid_weak_deg": 90, "plaid_strong_deg": 0, "probe_ori": 135},
]

# Fixation
fixation = Symbol(shape="cross", color="#4d4d4d", duration=200)

# Gray ring placeholder
placeholder = Symbol(
    items=[
        {
            "shape": "ring",
            "innerRadius": R_INNER,
            "outerRadius": R_OUTER,
            "color": GRAY55,
        }
    ],
    duration=80,
)

# Prime: circle filled with oriented stripes
prime = Symbol(
    items=[
        {
            "shape": "circle",
            "radius": R_INNER,
            "color": "#777",
            "texture": {
                "type": "stripes",
                "bar": BAR_PX,
                "duty": 0.5,
                "angle": TimelineVariable("prime_deg"),
            },
        }
    ],
    duration=100,
)

# Plaid: multiply two stripe-filled circles + overlay the ring
plaid = Symbol(
    items=[
        {
            "shape": "circle",
            "radius": R_INNER,
            "color": "#777",
            "blend": "multiply",
            "texture": {
                "type": "stripes",
                "bar": BAR_PX,
                "duty": 0.5,
                "angle": TimelineVariable("plaid_weak_deg"),
                "colors": WEAK_COLORS,
            },
        },
        {
            "shape": "circle",
            "radius": R_INNER,
            "color": "#777",
            "blend": "multiply",
            "texture": {
                "type": "stripes",
                "bar": BAR_PX,
                "duty": 0.5,
                "angle": TimelineVariable("plaid_strong_deg"),
                "colors": STRONG_COLORS,
            },
        },
        {
            "shape": "ring",
            "innerRadius": R_INNER,
            "outerRadius": R_OUTER,
            "color": GRAY55,
            "z": 10,
        },
    ],
    duration=80,
)

# Mask: circle filled with noise + ring overlay
mask = Symbol(
    items=[
        {
            "shape": "circle",
            "radius": R_INNER,
            "color": "#777",
            "texture": {
                "type": "noise",
                "cell": 6,
                "seed": 1337,
                "mix": 0.6,
                "colors": ["#333", "#ccc"],
            },
        },
        {
            "shape": "ring",
            "innerRadius": R_INNER,
            "outerRadius": R_OUTER,
            "color": GRAY55,
            "z": 10,
        },
    ],
    duration=500,
)


# Forced-choice (left/right) correctness
def is_correct(darker_strong_deg):
    return "f" if darker_strong_deg == 135 else "j"


correct_key_left_right = FunctionVariable(
    name="correct_key", fct=is_correct, args=[TimelineVariable("plaid_strong_deg")]
)

resp_left_right = Text(
    text=(
        "Which orientation was darker?<br>F = Left-leaning &nbsp;&nbsp; J = Right-leaning"
    ),
    choices=["f", "j"],
    correct_key=correct_key_left_right,
)

# Feedback
feedback = Feedback(duration=1000)

# Probe: a thin rotated rectangle (was 'stripe')
probe_stripe = Symbol(
    items=[
        {
            "shape": "rectangle",
            "width": 10,
            "height": 600,
            "rotation": TimelineVariable("probe_ori"),
            "color": "#999",
        },
        {
            "shape": "circle",
            "radius": R_INNER,
            "color": "#777",
            "texture": {
                "type": "noise",
                "cell": 6,
                "seed": 2024,
                "mix": 0.6,
                "colors": ["#333", "#ccc"],
            },
        },
        {
            "shape": "ring",
            "innerRadius": R_INNER,
            "outerRadius": R_OUTER,
            "color": GRAY55,
            "z": 10,
        },
    ],
    duration=500,
)


# Same/Different correctness
def is_same(probe_ori, plaid_strong_deg):
    return "f" if probe_ori == plaid_strong_deg else "j"


correct_key_same_diff = FunctionVariable(
    name="correct_key",
    fct=is_same,
    args=[TimelineVariable("probe_ori"), TimelineVariable("plaid_strong_deg")],
)

resp_same_diff = Text(
    text=(
        "Is the outer gray stripe in the same direction as the darker set of lines?<br>"
        "F = Same &nbsp;&nbsp; J = Different"
    ),
    choices=["f", "j"],
    correct_key=correct_key_same_diff,
)

# ----------- Build and export -----------
trial_sequence_left_right = [
    fixation,
    placeholder,
    prime,
    plaid,
    mask,
    resp_left_right,
    feedback,
]
trial_sequence_same_diff = [
    fixation,
    placeholder,
    prime,
    plaid,
    mask,
    probe_stripe,
    resp_same_diff,
    feedback,
]

block_left_right = Block(trial_sequence_left_right, timeline_left_right)
block_same_diff = Block(trial_sequence_same_diff, timeline_same_diff)

Experiment([block_left_right, block_same_diff]).to_html("plaid_demo.html")
