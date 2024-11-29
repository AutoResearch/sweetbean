from abc import ABC, abstractmethod
from typing import List

from sweetbean_v2.datatype.variables import to_js


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
        self.to_js()

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

    response_key = "response"

    def _process_response(self):
        self.js_data += (
            f'data["bean_correct"]='
            f'data["bean_correct_key"]===data["{self.response_key}"];'
        )


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
