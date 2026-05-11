"""
This script demonstrates how to use the `run_on_language` method to run an experiment
with image stimuli.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import Image

stim_1 = Image(
    stimulus="https://media.istockphoto.com/id/120492078/photo/"
    "banana.jpg?s=1024x1024&w=is&k=20&c=M9KLVNgqLft_btWgSu0iZAmdv2asI11Qel-6fsQK140=",
    choices=[" "],
)

block = Block([stim_1])
experiment = Experiment([block])

# To make this work, there is a file called image_prompts.json in the same directory as this
# script with the following content:
# {
# "https://media.istockphoto.com/id/120492078/photo/banana.jpg?s=1024x1024&w=is&k=20&c=M9KLVNgqLft_btWgSu0iZAmdv2asI11Qel-6fsQK140=": "You see a picture of a banana."   # noqa: E501
# }

experiment.run_on_language()
