from sweetbean import Block, Experiment
from sweetbean.stimulus.Gabor import Gabor

gabor_1 = Gabor(
    canvas_width=900,
    canvas_height=540,
    bg_gray=0.5,
    gamma=1.0,
    patches=[
        # left
        dict(
            x_px=-220,
            y_px=0,
            sigma_px=42,
            sf_cpp=0.02,
            orientation_deg=45,
            phase_deg=0,
            contrast=0.40,
            label="left",
        ),
        # right
        dict(
            x_px=220,
            y_px=0,
            sigma_px=42,
            sf_cpp=0.02,
            orientation_deg=135,
            phase_deg=180,
            contrast=0.55,
            label="right",
        ),
    ],
    response_keys=["f", "j"],
    keymap_to_patch_index={"f": 0, "j": 1},
    end_on_response=True,
    duration=750,  # alias for trial_duration
)

gabor_2 = Gabor(
    patches=[
        dict(
            x_px=0,
            y_px=0,
            sigma_px=20,
            sf_cpp=0.02,
            orientation_deg=0,
            phase_deg=0,
            contrast=0.55,
        )
    ]
)

block = Block([gabor_1, gabor_2])
experiment = Experiment([block])
experiment.to_html("gabor.html")
