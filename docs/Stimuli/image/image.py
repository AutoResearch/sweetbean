from sweetbean import Block, Experiment
from sweetbean.stimulus import Image

stim_1 = Image(
    stimulus="https://media.istockphoto.com/id/120492078/photo/"
    "banana.jpg?s=1024x1024&w=is&k=20&c=M9KLVNgqLft_btWgSu0iZAmdv2asI11Qel-6fsQK140=",
    choices=[" "],
)

trial_sequence = Block([stim_1])
experiment = Experiment([trial_sequence])
experiment.to_html("image.html")
