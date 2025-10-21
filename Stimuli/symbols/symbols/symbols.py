from sweetbean import Block, Experiment
from sweetbean.stimulus import Symbol, Text

stim_1 = Text(
    text="Welcome! We show some Symbols. Press SPACE to continue", choices=[" "]
)

stim_2 = Symbol(
    shape="rectangle", color="#f0f", duration=1000, choices=["f", "j"], correct_key="f"
)
stim_3 = Symbol(
    shape="triangle", color="red", duration=1000, choices=["f", "j"], correct_key="f"
)
stim_4 = Symbol(
    shape="circle", color="green", duration=1000, choices=["f", "j"], correct_key="j"
)

block = Block([stim_1, stim_2, stim_3, stim_4])

Experiment([block]).to_html("symbols.html")
