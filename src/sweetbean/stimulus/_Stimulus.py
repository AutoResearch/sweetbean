import warnings
from abc import ABC, abstractmethod
from typing import Optional, TypeVar

from jinja2 import Template

from sweetbean.parameter import param_to_psych


class Stimulus(ABC):
    """
    A base class for stimuli
    """

    text_js = "{"
    text_trial = ""
    text_data = "on_finish: (data) => {"
    template: Optional[str] = None
    base_template: Optional[str] = None
    choices_template: Optional[str] = None
    duration_template: Optional[str] = None

    def __init__(self, args):
        if "self" in args:
            del args["self"]
        if "__class__" in args:
            del args["__class__"]
        self.arg = args
        self.arg_js = {}
        for key in args:
            self.arg_js[key] = param_to_psych(args[key])
        self.to_psych()

    @classmethod
    def set_base_template(cls, template):
        cls.base_template = template

    @classmethod
    def set_duration_template(cls, template):
        cls.duration_template = template

    @classmethod
    def set_choices_template(cls, template):
        cls.choices_template = template

    def _type_to_psych(self):
        self.text_trial += f'type: {self.arg["type"]},'
        self.text_data += f'data["bean_type"] = \'{self.arg["type"]}\';'

    def _duration_to_psych(self):
        if "duration" in self.arg and self.arg["duration"] is not None:
            self.text_trial += self._set_param_js_preamble("trial_duration")
            self.text_trial += self._set_set_variable("duration")
            self.text_trial += "return "
            self.text_trial += self._set_get_variable("duration") + "},"
            self._set_data_text("duration")

    @abstractmethod
    def _stimulus_to_psych(self):
        pass

    def show(self, show_duration=True, **kwargs):
        self.check_flags(kwargs)
        if self.template is None:
            if self.base_template is None:
                raise ValueError(f"No template set for this stimulus {self}")
            if self.duration_template is None:
                self.duration_template = (
                    "{% if duration %} for {{ duration }} ms{% endif %}"
                )
            if self.choices_template is None:
                self.choices_template = (
                    "{% if choices %} You can press {{ choices }}. "
                    "You press <<{% endif %}"
                )
            self.template = " " + self.base_template
            if show_duration:
                self.template += self.duration_template
            self.template += "."
            self.template += self.choices_template
        return Template(self.template).render(kwargs)

    def _choices_to_psych(self):
        if "choices" in self.arg and self.arg["choices"] is not None:
            self.text_trial += self._set_param_js_preamble("choices")
            self.text_trial += self._set_set_variable("choices")
            self.text_trial += "return "
            self.text_trial += self._set_get_variable("choices") + "},"
            self._set_data_text("choices")

    def _set_param_full(self, name):
        if name in self.arg and self.arg[name] is not None:
            self.text_trial += self._set_param_js_preamble(name)
            self.text_trial += self._set_set_variable(name)
            self.text_trial += "return "
            self.text_trial += self._set_get_variable(name) + "},"
            self._set_data_text(name)

    def _correct_to_psych(self):
        if "correct_key" in self.arg:
            self._set_data_text("correct_key")
            self.text_data += self._set_set_variable("correct")
            self.text_data += (
                'data["bean_correct"] = '
                + self._set_get_variable("correct_key")
                + '== data["response"]'
            )

    def to_psych(self):
        self._type_to_psych()
        self._duration_to_psych()
        self._stimulus_to_psych()
        self._choices_to_psych()
        self._correct_to_psych()
        self.text_js += self.text_trial + self.text_data + "}}"

    def to_image(self):
        pass

    def _set_param_js_preamble(self, param):
        return f"{param}: () => " + "{"

    def _set_data_text(self, param):
        self.text_data += self._set_set_variable(param)
        self.text_data += (
            f'data["bean_{param}"] = ' + self._set_get_variable(param) + ";"
        )

    def _set_set_variable(self, key):
        if key not in self.arg_js:
            return ""

        return f"let {key} = " + str(self.arg_js[key]) + ";"

    def check_flags(self, dict):
        # Check each attribute for flagged values
        for attr_name in dir(self):
            attr = getattr(self.__class__, attr_name, None)
            if callable(attr) and hasattr(attr, "test_language"):
                value = dict[attr_name]
                if attr.test_language(value):
                    warnings.warn(
                        f"Warning: {attr_name} is set to {value}, "
                        f"which may not be implemented for templating.",
                        UserWarning,
                    )

    def _set_get_variable(self, key):
        if key not in self.arg_js:
            return ""
        if isinstance(self.arg_js[key], str) and self.arg_js[key].startswith("()"):
            return f"{key}()"
        return f"{key}"

    def set_template(self, template):
        self.template = template


StimulusVar = TypeVar("StimulusVar", bound=Stimulus)
