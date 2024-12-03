from sweetbean import Block, Experiment
from sweetbean.stimulus import Image

stim_1 = Image(
    stimulus="https://media.istockphoto.com/id/120492078/photo/"
    "banana.jpg?s=1024x1024&w=is&k=20&c=M9KLVNgqLft_btWgSu0iZAmdv2asI11Qel-6fsQK140=",
    choices=[" "],
)

block = Block([stim_1])

# Create an image of the stimulus
block.to_image("./", data=None, sequence=False, timeline_idx="random", zoom_factor=1)

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("image.html")
