from abc import ABC, abstractmethod
from typing import List, Union

from jinja2 import Template

from sweetbean.util.parse import to_js
from sweetbean.variable import (
    DataVariable,
    FunctionVariable,
    SharedVariable,
    TimelineVariable,
)


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
    l_args: dict = {}
    l_ses: dict = {}

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

    def return_shared_variables(self):
        shared_variables = {}

        def extract_shared_variables(value):
            if isinstance(value, SharedVariable):
                shared_variables[value.name] = value
            elif isinstance(value, dict):
                for v in value.values():
                    extract_shared_variables(v)
            elif isinstance(value, list):
                for item in value:
                    extract_shared_variables(item)
            elif isinstance(value, FunctionVariable):
                for arg in value.args:
                    extract_shared_variables(arg)

        if self.l_args:
            for key in self.arg:
                extract_shared_variables(self.arg[key])
        if self.side_effects:
            for se in self.side_effects:
                extract_shared_variables(se.get_variable)
                extract_shared_variables(se.set_variable)
        return shared_variables

    def to_js(self):
        self.js = ""
        self.js_data = ""
        self.js_before = ""
        self.js_body = ""
        self._params_to_js()
        self.js = (
            f"{{{self.js_body}{self.js_before}on_finish:(data)=>{{{self.js_data}}}}}"
        )

    def to_js_for_image(self):
        self.js = ""
        self.js_data = ""
        self.js_before = ""
        self.js_body = ""
        self._params_to_js_from_prepared()
        self.js = (
            f"{{{self.js_body}{self.js_before}on_finish:(data)=>{{{self.js_data}}}}}"
        )

    def _params_to_js(self):
        self.js_body += f'type: {self.arg["type"]},'
        for key in self.arg_js:
            self._param_to_js(key, self.arg_js[key])
        for key in self.arg:
            if key not in self.arg_js:
                self._param_to_js_arg(key, self.arg[key])
        self._add_special_param()
        self._process_response()
        self._set_before()
        if self.side_effects:
            self._set_side_effects()

    def _params_to_js_from_prepared(self):
        self.js_body += f'type: {self.arg["type"]},'
        for key in self.l_args:
            self._param_to_js(key, self.l_args[key])
        self._add_special_param()
        self._process_response()
        self._set_before()
        if self.side_effects:
            self._set_side_effects()

    def _prepare_args_l(self, timeline_element, data, shared_variables, datum=None):
        if not datum:
            self.l_args = {}
            self.l_ses = {}
            for key, value in self.arg.items():
                key_ = key
                value_ = _parse_variable(
                    value, timeline_element, data, shared_variables
                )
                self.l_args[key_] = value_
        else:
            for key, value in datum.items():
                self.l_args[key] = value

    def _resolve_side_effects(self, timeline_element, data, shared_variables):
        if self.side_effects:
            for se in self.side_effects:
                get_variable = _parse_variable(
                    se.get_variable, timeline_element, data, shared_variables, se=True
                )
                self.l_ses[se.set_variable.name] = get_variable

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        prompts.append(self._get_prompt_l())
        prompt_response = self._get_response_prompt_l()
        s_data = {}
        data = self.l_args.copy()
        if prompt_response:
            prompts[-1] += " " + prompt_response
            if multi_turn:
                _in_prompt = prompts[-1]
            else:
                _in_prompt = " ".join([p for p in prompts])
            if not datum:
                _r = get_input(_in_prompt)
                if isinstance(_r, str):
                    response = _r.upper()
                elif isinstance(_r, dict):
                    if "response" not in _r:
                        raise Exception(f"{_r} has an invalid response format")
                    response = _r["response"].upper()
                else:
                    raise Exception(f"{_r} has an invalid response format")
                # response = get_input(_in_prompt).upper()
            else:
                _r = datum["response"].upper()
                response = _r
            s_data = self._process_response_l(_r)
            prompts[-1] += f"{response}>>"
        data.update(s_data)
        return data, prompts

    def _get_prompt_l(self):
        if self.l_template is None:
            raise Exception("No template or function set for getting prompt")
        return Template(self.l_template).render(self.l_args)

    def _get_response_prompt_l(self):
        raise Exception("No template or function set for getting response prompt")

    def _process_response_l(self, response):
        if isinstance(response, dict):
            return response
        return {"response": response.upper()}

    def _param_to_js(self, key, param):
        body, data = _set_param_js(key, param)
        if key not in self.excludes and key != "type" and key != "duration":
            self.js_body += body
        self.js_data += data

    def _param_to_js_arg(self, key, param):
        _, data = _set_param_js(key, param)
        self.js_data += data

    def _set_side_effects(self):
        for se in self.side_effects:
            self.js_data += se.to_js()
            if not isinstance(se.set_variable, DataVariable):
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

    def _get_response_prompt_l(self):
        if not self.l_args["choices"]:
            return None
        return Template(self.response_template).render(
            {"choices": [c.upper() for c in self.l_args["choices"]]}
        )

    def _process_response_l(self, response):
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


def _parse_variable(variable, timeline_element, data, shared_variables, se=False):
    if isinstance(variable, list):
        return [
            _parse_variable(a, timeline_element, data, shared_variables, se)
            for a in variable
        ]
    if isinstance(variable, dict):
        return {
            k: _parse_variable(v, timeline_element, data, shared_variables, se)
            for k, v in variable.items()
        }
    if isinstance(variable, tuple):
        return tuple(
            _parse_variable(a, timeline_element, data, shared_variables, se)
            for a in variable
        )
    if isinstance(variable, TimelineVariable):
        return timeline_element[variable.name]
    if isinstance(variable, DataVariable):
        if se:
            return data[-variable.window - 1][variable.raw_name]
        return data[-variable.window][variable.raw_name]
    if isinstance(variable, FunctionVariable):
        _args = [
            _parse_variable(a, timeline_element, data, shared_variables, se)
            for a in variable.args
        ]
        return variable.fct(*_args)
    if isinstance(variable, SharedVariable):
        return shared_variables[variable.name]

    return variable
