# Automated Generation of Stimulus Sequence Figures

![stimulus_sequence](../img/stimuli/flanker.png)

SweetBea allows you to automatically generate an image of the stimulus sequence often used in the method section of a paper with a single line of code. This feature is designed to streamline the process of creating the method section of a paper.

Assume you have the following block of code representing a Flanker task:
```python
from sweetbean import Block
from sweetbean.stimulus import Blank, Feedback, Fixation, Flanker
from sweetbean.variable import TimelineVariable

timeline = [
    {"direction": "left", "distractor": "right", "correct_key": "f"},
    {"direction": "right", "distractor": "right", "correct_key": "j"},
    {"direction": "left", "distractor": "left", "correct_key": "f"},
    {"direction": "right", "distractor": "left", "correct_key": "j"},
]

direction = TimelineVariable("direction")
distractor = TimelineVariable("distractor")
correct_key = TimelineVariable("correct_key")

fixation = Fixation(1000)
so_s = Blank(400)
flanker = Flanker(2000, direction, distractor, ["j", "f"], correct_key)
so_f = Blank(300)
feedback = Feedback(800, window=2)

block = Block([fixation, so_s, flanker, so_f, feedback], timeline)
```

You can generate an image of the stimulus sequence with the following line of code:
```python
block.to_image(path='stimulus_sequence.png', data=[None, None, {'correct': True}, None, None], sequence=True, timeline_idx='random', zoom_factor=3)
```

The `to_image` method takes the following arguments:
- `path`: The path to save the image. If the path is set to None, the function will return a PIL image object.
- `data`: In this case the feedback stimulus expects the `correct` value of the flanker stimulus to be set. In a real experiment, this would be determined by the response of the participant. Here, we manually set it to `True`.
- `sequence`: Whether to create one image with the sequence of stimuli or multiple images with each stimulus (then the path should be a directory).
- `timeline_idx`: The index of the timeline element to use for the image. In this case, we set it to `random` to randomly select a timeline element. It could also be set to a specific index or None to create the image from the full timeline.
- `zoom_factor`: The factor by which to zoom the stimulus (often the stimulus is in the middle of the screen with a large margin). The default is 3. This can also be set as a list to define different zoom factor for each stimulus.