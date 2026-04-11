from sweetbean.stimulus.Stimulus import _BaseStimulus


class HtmlSliderResponse(_BaseStimulus):
    """HTML slider response stimulus (jsPsych html-slider-response plugin)."""

    type = "jsPsychHtmlSliderResponse"

    def __init__(
        self,
        duration=None,
        stimulus="",
        min=0.0,
        max=100.0,
        slider_start=50.0,
        step=None,
        labels=None,
        button_label="Continue",
        require_movement=False,
        response_ends_trial=True,
        correct_values=None,
        correct_min=None,
        correct_max=None,
        side_effects=None,
    ):
        if labels is None:
            labels = []
        if correct_values is None:
            correct_values = []
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_response"]=data["response"];'
        self.js_data += 'data["bean_rt"]=data["rt"];'

        correct_values = self.arg.get("correct_values", [])
        correct_min = self.arg.get("correct_min", None)
        correct_max = self.arg.get("correct_max", None)
        if correct_values:
            vals = ",".join(str(float(v)) for v in correct_values)
            self.js_data += f'let _sb_correct_values=[{vals}];'
            self.js_data += 'data["bean_correct"]=_sb_correct_values.includes(data["response"]);'
        elif correct_min is not None and correct_max is not None:
            lo = float(correct_min)
            hi = float(correct_max)
            self.js_data += f'data["bean_correct"]=(data["response"]>={lo}&&data["response"]<={hi});'
        else:
            self.js_data += 'data["bean_correct"]=null;'

    def _set_before(self):
        pass
