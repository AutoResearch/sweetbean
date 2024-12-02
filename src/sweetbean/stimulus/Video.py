from sweetbean.stimulus.Stimulus import _KeyboardResponseStimulus


class Video(_KeyboardResponseStimulus):
    """
    shows a video
    """

    type = "jsPsychImageKeyboardResponse"

    def __init__(
        self,
        duration=0,
        src="",
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the image
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            side_effects: a dictionary of side effects
        """
        super().__init__(locals(), side_effects=side_effects)

    def _add_special_param(self):
        pass

    def _set_before(self):
        pass
