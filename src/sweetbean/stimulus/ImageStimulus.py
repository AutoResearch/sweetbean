from typing import List

from sweetbean.stimulus._Stimulus import Stimulus
from sweetbean.stimulus._utils import IntType


class ImageStimulus(Stimulus):
    """
    shows an image
    """

    def __init__(
        self,
        duration: IntType = None,
        src: str = "",
        choices: List[str] = [],
        correct_key: str = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the image
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychImageKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("src")
        self.text_trial += "return "
        self.text_trial += self._set_get_variable("src") + "},"
        self._set_data_text("src")
