"""
The rok 'press a or b or wait' is shown in pink for 2000ms. The allowed responses are 'a' and 'b'.
"""

from sweetbean_v2 import Block, Experiment
from sweetbean_v2.stimulus import ROK

# EVENT SEQUENCE

rok = ROK(
    duration=100000,
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
experiment = Experiment([block])

experiment.to_html("basic.html")