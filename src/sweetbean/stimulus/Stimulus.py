from abc import ABC, abstractmethod
from typing import Any, List, Union

from jinja2 import Template

from sweetbean.util.parse import to_js
from sweetbean.variable import DataVariable, FunctionVariable, TimelineVariable


class _BaseStimulus(ABC):
    """
    A base class for stimuli
    """

    js = ""
    js_body = ""
    js_before = ""
    js_data = ""
    excludes: List[str] = []
    type = ""
    l_template: Union[str, None] = None
    l_args: List[Any] = []

    def __init__(self, args, side_effects=None):
        self.side_effects = side_effects
        if "self" in args:
            del args["self"]
        if "__class__" in args:
            del args["__class__"]
        if "side_effects" in args:
            del args["side_effects"]
        self.arg = args
        self.arg.update({"type": self.type})
        self.arg_js = {}
        if "duration" in self.arg:
            self.arg_js["trial_duration"] = self.arg["duration"]
        for key in self.arg:
            self.arg_js[key] = args[key]
        # self.to_js()

    def to_js(self):
        self.js = ""
        self.js_data = ""
        self.js_before = ""
        self.js_body = ""
        self._params_to_js()
        self.js = (
            f"{{{self.js_body}{self.js_before}on_finish:(data)=>{{{self.js_data}}}}}"
        )

    def _params_to_js(self):
        self.js_body += f'type: {self.arg["type"]},'
        for key in self.arg_js:
            self._param_to_js(key, self.arg_js[key])
        self._add_special_param()
        self._process_response()
        self._set_before()
        if self.side_effects:
            self._set_side_effects()

    def prepare_l_args(self, timeline_element, data):
        self.l_args = {}
        for key, value in self.arg.items():
            key_ = key
            value_ = _parse_variable(value, timeline_element, data)
            self.l_args[key_] = value_

    def get_prompt(self):
        if self.l_template is None:
            return self.l_args
        return Template(self.l_template).render(self.l_args)

    def get_response_prompt(self):
        return ""

    def _param_to_js(self, key, param):
        body, data = _set_param_js(key, param)
        if key not in self.excludes and key != "type" and key != "duration":
            self.js_body += body
        self.js_data += data

    def _set_side_effects(self):
        for se in self.side_effects:
            self.js_data += se.to_js()
            self.js_data += (
                f'data["bean_{se.set_variable.name}"]={se.set_variable.name};'
            )

    @abstractmethod
    def _add_special_param(self):
        pass

    @abstractmethod
    def _process_response(self):
        pass

    @abstractmethod
    def _set_before(self):
        pass


class _KeyboardResponseStimulus(_BaseStimulus, ABC):
    """
    A base class for stimuli that require a correct key and choices
    """

    response_template = "You can press {{ choices }}. You press <<"

    response_key = "response"

    def _process_response(self):
        self.js_data += (
            f'data["bean_correct"]='
            f'data["bean_correct_key"]===data["{self.response_key}"];'
        )

    def get_response_prompt(self):
        if not self.l_args["choices"]:
            return None
        return Template(self.response_template).render(
            {"choices": [c.upper() for c in self.l_args["choices"]]}
        )

    def process_response(self, response):
        if not self.l_args["correct_key"]:
            return {"response": response.upper(), "correct": None}
        return {
            "response": response.upper(),
            "correct": response.upper() == self.l_args["correct_key"].upper(),
        }


def _set_param_js(key, param):
    body = _set_param_preamble(key)
    body += _set_set_variable(key, param)
    body += "return "
    body += _set_get_variable(key) + "},"
    data = _set_data_text(key, param)
    return body, data


def _set_param_preamble(param):
    return f"{param}:()=>{{"


def _set_set_variable(key, param):
    return f"let {key}={to_js(param)};"


def _set_get_variable(key):
    return f"{key}"


def _set_data_text(key, param):
    res = ""
    res += _set_set_variable(key, param)
    res += f'data["bean_{key}"]={_set_get_variable(key)};'
    return res


def _parse_variable(variable, timeline_element, data):
    if isinstance(variable, list):
        return [_parse_variable(a, timeline_element, data) for a in variable]
    if isinstance(variable, dict):
        return {
            k: _parse_variable(v, timeline_element, data) for k, v in variable.items()
        }
    if isinstance(variable, tuple):
        return tuple(_parse_variable(a, timeline_element, data) for a in variable)
    if isinstance(variable, TimelineVariable):
        return timeline_element[variable.name]
    if isinstance(variable, DataVariable):
        if variable.window < 1:
            raise Exception("Window cannot be bellow 1")
        return data[-variable.window][variable.raw_name]
    if isinstance(variable, FunctionVariable):
        _args = [_parse_variable(a, timeline_element, data) for a in variable.args]
        return variable.fct(*_args)
    return variable
