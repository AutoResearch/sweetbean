"""
The rok 'press a or b or wait' is shown in pink for 2000ms. The allowed responses are 'a' and 'b'.
"""

from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import ROKStimulus

# EVENT SEQUENCE

rok = ROKStimulus(
    duration=100000,
    number_of_oobs=500,
    coherent_movement_direction=100,
    coherent_orientation=0,
    coherence_movement=50,
    coherence_orientation=90,
)

event_sequence = [rok]

# BLOCK DESIGN

block = Block(event_sequence)
experiment = Experiment([block])

experiment.to_html("basic.html")
