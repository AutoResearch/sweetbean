from typing import Union

from sweetbean.parameter import DerivedParameter, TimelineVariable
from sweetbean.stimulus._Stimulus import Stimulus


class ChoiceStimulus(Stimulus):
    """
    html elements that can be used to present a choice
    """

    def __init__(
        self,
        duration: Union[None, int, TimelineVariable, DerivedParameter] = None,
        html_array=None,
        values=None,
        time_after_stimulus=0,
    ):
        if values is None:
            values = [0, 1]
        if html_array is None:
            html_array = [
                '<div style="position: absolute; top:40vh; left:20vw; '
                'width: 20vw; height: 20vh; background: blue"</div>',
                '<div style="position: absolute; top:40vh; right:20vw; '
                'width: 20vw; height: 20vh; background: red"</div>',
            ]
        type = "jsPsychHtmlChoice"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self._set_param_full("html_array")
        self._set_param_full("values")
        self._set_param_full("time_after_stimulus")

    def _correct_to_psych(self):
        self.text_data += self._set_set_variable("value")
        self.text_data += 'data["bean_value"] = data["value"]'
        self.text_data += self._set_set_variable("choice")
        self.text_data += 'data["bean_choice"] = data["choice"]'
