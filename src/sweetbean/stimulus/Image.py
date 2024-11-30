from sweetbean.stimulus.Stimulus import _KeyboardResponseStimulus


class Image(_KeyboardResponseStimulus):
    """
    shows an image
    """

    type = "jsPsychImageKeyboardResponse"

    def __init__(
        self,
        duration=None,
        stimulus="",
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
        """
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _set_before(self):
        pass
