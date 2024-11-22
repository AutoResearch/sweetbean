from sweetbean.stimulus._Stimulus import Stimulus


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


class MultiChoiceSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyMultiChoice"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': Object.keys(p)[0],"
        self.text_trial += "options: p[Object.keys(p)[0]]})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")


class LikertSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyLikert"
        super().__init__(locals())

    @classmethod
    def from_scale(cls, prompts=[], scale=[]):
        prompts_ = []
        for p in prompts:
            prompts_.append({p: scale})
        return cls(prompts_)

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': Object.keys(p)[0],"
        self.text_trial += "labels: p[Object.keys(p)[0]]})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")
