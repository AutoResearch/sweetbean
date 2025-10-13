from typing import List, Optional, Union

from sweetbean.stimulus.Stimulus import _KeyboardResponseStimulus


class Video(_KeyboardResponseStimulus):
    """
    shows a video
    """

    # correct jsPsych plugin id
    type = "jsPsychVideoKeyboardResponse"

    def __init__(
        self,
        duration: Optional[int] = None,  # alias for trial_duration
        stimulus: Optional[
            Union[str, List[str]]
        ] = None,  # single URL/path or list of sources
        choices=None,  # e.g., ["f","j"] | "ALL" | "NO_KEYS"
        correct_key: str = "",
        trial_ends_after_video: bool = True,
        autoplay: bool = True,
        controls: bool = False,
        width: Optional[int] = None,
        height: Optional[int] = None,
        muted: bool = True,  # helpful for autoplay policies
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented (alias for trial_duration)
            stimulus: video source(s). Either a single string or a list of strings (URLs/paths).
                 You can specify multiple formats of the same video (e.g., .mp4, .ogg, .webm)
                 to maximize the cross-browser compatibility.
            choices: keys to accept (e.g., ["f","j"]), or "ALL" / "NO_KEYS"
            correct_key: the correct key to press (optional)
            trial_ends_after_video: end the trial automatically when video finishes
            autoplay: start playback automatically
            controls: show native video controls
            width, height: optional pixel dimensions
            muted: mute audio (often required for autoplay)
            side_effects: a dictionary of side effects
        """
        if isinstance(stimulus, str):
            stimulus = [stimulus]
        super().__init__(locals(), side_effects=side_effects)

    def _add_special_param(self):
        # duration -> trial_duration (SweetBean convention)
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

        # Normalize stimulus to a list[str] for jsPsych video plugin
        stim = self.arg_js.get("stimulus")
        if isinstance(stim, str) and stim:
            self.arg_js["stimulus"] = [stim]
        elif isinstance(stim, list):
            # leave as-is (assumed list[str])
            pass
        # else: leave None; jsPsych will error if missing, which is fine for dev feedback

        # Keep declarative type
        self.arg_js["type"] = self.type

    def _process_response(self):
        # convenience mirrors to align with other keyboard-response wrappers
        self.js_data += 'data["bean_key"] = data["key_press"];'
        self.js_data += 'data["bean_rt"] = data["rt"];'

    def _set_before(self):
        pass
