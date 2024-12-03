"""
The rok presents orientated objects (triangles).
50% of them move in an angle of 100deg and 50% randomly.
90% of them are orientated to the right and 10% randomly.
"""

from sweetbean import Block, Experiment
from sweetbean.stimulus import ROK

# EVENT SEQUENCE

rok = ROK(
    duration=3000,
    number_of_oobs=500,
    coherent_movement_direction=100,
    coherent_orientation=0,
    coherence_movement=50,
    coherence_orientation=90,
    movement_speed=10,
)

event_sequence = [rok]

# BLOCK DESIGN

block = Block(event_sequence)

# Create an image of the stimuli
block.to_image("./", data=None, sequence=False, timeline_idx="random", zoom_factor=1)

# Create an HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("rok.html")
