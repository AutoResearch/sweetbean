# docs/Stimuli/video/basic.py

from sweetbean import Block, Experiment
from sweetbean.stimulus import Text, Video

# Gate: require a keypress so browsers allow autoplay
gate = Text(
    text="Press SPACE to start the videos",
    color="white",
    choices=[" "],  # spacebar
    duration=None,
)


# Example 1 — play a video from a URL; trial ends when the video finishes.
video_trial = Video(
    stimulus="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    choices=["f", "j"],  # collect keypress during playback
    trial_ends_after_video=True,  # end automatically at video end
    autoplay=True,
    controls=False,
    width=640,
    height=360,
)

# Example 2 — allow a 2s response window after the video ends.
post_window = Video(
    stimulus="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    choices=["f", "j"],
    trial_ends_after_video=False,  # don't end on finish
    duration=2000,  # alias for trial_duration (keeps trial alive 2s)
    autoplay=True,
    controls=False,
)

# Example 3 — multiple sources (browser compatibility); still OK with URLs.
multi_source = Video(
    stimulus=[
        "https://media.w3.org/2010/05/sintel/trailer.webm",
        "https://media.w3.org/2010/05/sintel/trailer.mp4",
    ],
    choices=["f", "j"],
    trial_ends_after_video=True,
    autoplay=True,
    controls=True,
)

block = Block([gate, video_trial, post_window, multi_source])
experiment = Experiment([block])
experiment.to_html("video.html")
