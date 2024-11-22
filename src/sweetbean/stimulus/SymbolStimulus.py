from typing import List

from sweetbean.stimulus._Stimulus import Stimulus
from sweetbean.stimulus._utils import IntType


class SymbolStimulus(Stimulus):
    """
    show a symbol
    """

    base_template = "You see a {{ color}} {{ symbol }}"

    def __init__(
        self,
        duration: IntType = None,
        symbol: str = "",
        color: str = "white",
        choices: List[str] = [],
        correct_key: str = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            symbol: the symbol to show (allowed: square, triangle, circle)
            color: the color of the symbol
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychHtmlKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("symbol")
        self.text_trial += self._set_set_variable("color")
        self.text_trial += "return "
        self.text_trial += (
            f'"<div class=\'sweetbean-"+{self._set_get_variable("symbol")}+"\' '
            f'style=\'background-color: "+{self._set_get_variable("color")}+"\'></div>"'
            "},"
        )
        self._set_data_text("symbol")
        self._set_data_text("color")


class SurveyStimulus(Stimulus):
    def __init__(self, args):
        super().__init__(args)

    def to_psych(self):
        self._type_to_psych()
        self._stimulus_to_psych()
        self.text_js += self.text_trial + self.text_data + "}}"


class TextSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyText"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': p})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")
