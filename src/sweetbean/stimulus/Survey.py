from sweetbean.stimulus.Stimulus import _BaseStimulus
from sweetbean.variable import FunctionVariable


class _Survey(_BaseStimulus):
    """
    A base class for surveys
    """

    def __init__(self, questions=None, side_effects=None):
        super().__init__(locals(), side_effects=side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_response"]=data["response"];'

    def _set_before(self):
        pass


class TextSurvey(_Survey):
    """
    A survey that asks for text input
    """

    type = "jsPsychSurveyText"

    def __init__(self, questions=None, side_effects=None):
        """
        Arguments:
            questions: a list of strings representing the questions
            side_effects: a dictionary of side effects
        """
        if not questions:
            questions = []

        def get_prompts(_prompts):
            prompts_ = []
            for p in _prompts:
                prompts_.append({"prompt": p})
            return prompts_

        questions_ = FunctionVariable("questions", get_prompts, [questions])
        super().__init__(questions_, side_effects=side_effects)

    def process_l(self, prompts, get_input, multi_turn, datum=None):
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
            if not datum:
                response = get_input(_in_prompt)
            else:
                response = datum["response"][f"Q{str(idx)}"]
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q{str(idx)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts


class MultiChoiceSurvey(_Survey):
    """
    A survey that asks for multiple choice input
    """

    type = "jsPsychSurveyMultiChoice"

    def __init__(self, questions=None, side_effects=None):
        """
        Arguments:
            questions: a list of dictionaries with the keys "prompt" and "options"
            side_effects: a dictionary of side effects
        """
        if not questions:
            questions = []

        def get_prompts(_prompts):
            prompts_ = []
            for p in _prompts:
                prompts_.append({"prompt": p["prompt"], "options": p["options"]})
            return prompts_

        questions_ = FunctionVariable("questions", get_prompts, [questions])
        super().__init__(questions_, side_effects=side_effects)

    def process_l(self, prompts, get_input, multi_turn, datum=None):
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
            if not datum:
                response = get_input(_in_prompt)
            else:
                response = datum["response"][f"Q{str(idx)}"]
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q{str(idx)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts


#
#
class LikertSurvey(_Survey):
    """
    A survey that asks for Likert scale input
    """

    type = "jsPsychSurveyLikert"

    def __init__(self, questions=None, side_effects=None):
        """
        Arguments:
            questions: a list of dictionaries with the keys "prompt" and "labels"
            side_effects: a dictionary of side effects
        """
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
        """
        Create a LikertSurvey from a scale

        Arguments:
            prompts: a list of strings representing the prompts
            scale: a list of strings representing the scale
            side_effects: a dictionary of side effects
        """
        if not prompts:
            prompts = []
        if not scale:
            scale = []
        prompts_ = []
        for p in prompts:
            prompts_.append({"prompt": p, "labels": scale})
        return cls(prompts_, side_effects=side_effects)

    def process_l(self, prompts, get_input, multi_turn, datum=None):
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
            if not datum:
                response = get_input(_in_prompt)
            else:
                response = datum["response"][f"Q{str(idx)}"]
            current_prompt[-1] += f"<<{response}>>"
            responses[f"Q{str(idx)}"] = response
        data.update({"response": responses})
        prompts += current_prompt
        return data, prompts
