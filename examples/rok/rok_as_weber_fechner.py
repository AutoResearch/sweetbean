"""
The rok 'press a or b or wait' is shown in pink for 2000ms. The allowed responses are 'a' and 'b'.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import ROKStimulus

# EVENT SEQUENCE

rok = ROKStimulus(
    duration=100000,
    number_of_oobs=[10, 200],
    number_of_apertures=2,
    coherent_movement_direction=0,
    coherent_orientation=0,
    coherence_movement=0,
    coherence_orientation=0,
    movement_speed=0,
)

event_sequence = [rok]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])

experiment.to_html("rok_weber_fechner.html")
