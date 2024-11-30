from sweetbean_v2.datatype.variables import FunctionVariable
from sweetbean_v2.stimulus.Stimulus import _BaseStimulus


class _Survey(_BaseStimulus):
    def __init__(self, questions=None, side_effects=None):
        super().__init__(locals(), side_effects=side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_response"]=data["response"];'

    def _set_before(self):
        pass


class TextSurvey(_Survey):
    type = "jsPsychSurveyText"

    def __init__(self, questions=None, side_effects=None):
        if not questions:
            questions = []

        def get_prompts(_prompts):
            prompts_ = []
            for p in _prompts:
                prompts_.append({"prompt": p})
            return prompts_

        questions_ = FunctionVariable("questions", get_prompts, [questions])
        super().__init__(questions_, side_effects=side_effects)


class MultiChoiceSurvey(_Survey):
    type = "jsPsychSurveyMultiChoice"

    def __init__(self, questions=None, side_effects=None):
        if not questions:
            questions = []

        def get_prompts(_prompts):
            prompts_ = []
            for p in _prompts:
                prompts_.append({"prompt": p["prompt"], "options": p["options"]})
            return prompts_

        questions_ = FunctionVariable("questions", get_prompts, [questions])
        super().__init__(questions_, side_effects=side_effects)


#
#
class LikertSurvey(_Survey):
    type = "jsPsychSurveyLikert"

    def __init__(self, questions=None, side_effects=None):
        if not questions:
            questions = []

        def get_prompts(_prompts):
            prompts_ = []
            for p in _prompts:
                prompts_.append({"prompt": p["prompt"], "labels": p["labels"]})
            return prompts_

        questions_ = FunctionVariable("questions", get_prompts, [questions])
        super().__init__(questions_, side_effects=side_effects)

    #
    @classmethod
    def from_scale(cls, prompts=None, scale=None, side_effects=None):
        if not prompts:
            prompts = []
        if not scale:
            scale = []
        prompts_ = []
        for p in prompts:
            prompts_.append({"prompt": p, "labels": scale})
        return cls(prompts_, side_effects=side_effects)
