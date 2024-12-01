from sweetbean.stimulus.Stimulus import _BaseStimulus
from sweetbean.variable import FunctionVariable


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

    def process_l(self, prompts, get_input, multi_turn):
        current_prompt = []
        responses = {}
        data = self.l_args.copy()
        for idx, question in enumerate(self.l_args["questions"]):
            current_prompt.append(question["prompt"])
            if not multi_turn:
                _in_prompt = (
                    " ".join([p for p in prompts])
                    + " ".join([c for c in current_prompt])
                    + "<<"
                )
            else:
                _in_prompt = current_prompt[-1] + "<<"
            response = get_input(_in_prompt)
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q_{str(idx + 1)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts


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

    def process_l(self, prompts, get_input, multi_turn):
        current_prompt = []
        responses = {}
        data = self.l_args.copy()
        for idx, question in enumerate(self.l_args["questions"]):
            current_prompt.append(question["prompt"])
            current_prompt[-1] += " Your options are: " + ", ".join(
                [str(i) for i in question["options"]]
            )
            if not multi_turn:
                _in_prompt = (
                    " ".join([p for p in prompts])
                    + " ".join([c for c in current_prompt])
                    + "<<"
                )
            else:
                _in_prompt = current_prompt[-1] + "<<"
            response = get_input(_in_prompt)
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q{str(idx)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts


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

    def process_l(self, prompts, get_input, multi_turn):
        current_prompt = []
        responses = {}
        data = self.l_args.copy()
        for idx, question in enumerate(self.l_args["questions"]):
            current_prompt.append(question["prompt"])
            current_prompt[-1] += " Your options are: " + ", ".join(
                [str(i) for i in question["labels"]]
            )
            if not multi_turn:
                _in_prompt = (
                    " ".join([p for p in prompts])
                    + " ".join([c for c in current_prompt])
                    + "<<"
                )
            else:
                _in_prompt = current_prompt[-1] + "<<"
            response = get_input(_in_prompt)
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q_{str(idx + 1)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts
