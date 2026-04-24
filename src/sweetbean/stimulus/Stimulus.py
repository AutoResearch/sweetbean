import uuid
from abc import ABC, abstractmethod
from typing import List, Union

from jinja2 import Template

from sweetbean.extension.TouchButton import (
    TouchButton,
    collect_touch_buttons_from_function,
)
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
    _default_prompt_template: Union[str, None] = None
    l_args: dict = {}
    l_ses: dict = {}
    extensions = None
    # When True (the default), this stimulus's trial config emits an
    # `on_load` callback that calls `window.__sb_fit__(true)` to scale
    # `#jspsych-content` to fit the viewport (with body overflow hidden).
    # When False, the callback calls `window.__sb_fit__(false)` to clear
    # any prior scaling and restore body overflow:auto so the trial can
    # scroll naturally — the right default for text-heavy screens like
    # `InformedConsent`. Per-instance override: pass `fit_to_viewport=`
    # to any stimulus that exposes the kwarg, or set `stim.fit_to_viewport
    # = ...` after construction. See AUTHORING.md §"Auto-fit to viewport".
    fit_to_viewport: bool = True
    # Minimum response time in milliseconds. When > 0, the trial's
    # `on_load` installs a document-level capturing `keydown` listener
    # that calls `event.stopImmediatePropagation()` + `event.preventDefault()`
    # for the first `min_rt` ms, then removes itself. This blocks the
    # jsPsych keyboard-response plugin (or any other listener) from seeing
    # any key for that window, so participants cannot end the trial
    # before they have plausibly looked at the stimulus. Plugin-agnostic
    # because it's purely a DOM-level capture-phase swallow. The trial
    # itself is unmodified — once the gate elapses, normal jsPsych
    # listeners take over. Per-instance override: pass `min_rt=N` (ms) to
    # any stimulus that exposes the kwarg, or set `stim.min_rt = N` after
    # construction. See AUTHORING.md §"Minimum response time".
    min_rt: int = 0

    def __init__(self, args, side_effects=None):
        self.side_effects = side_effects
        if "self" in args:
            del args["self"]
        if "__class__" in args:
            del args["__class__"]
        if "side_effects" in args:
            del args["side_effects"]
        # Honor per-instance fit_to_viewport without polluting trial data.
        if "fit_to_viewport" in args:
            ftv = args.pop("fit_to_viewport")
            if ftv is not None:
                self.fit_to_viewport = bool(ftv)
        # Honor per-instance `min_rt` (ms response gate) without polluting
        # trial data. Negative or non-numeric values clamp to 0 so a
        # malformed override never throws inside the runner — `None`
        # means "use the class-level default".
        if "min_rt" in args:
            mr = args.pop("min_rt")
            if mr is not None:
                try:
                    self.min_rt = max(0, int(mr))
                except (TypeError, ValueError):
                    self.min_rt = 0
        self.arg = args
        self.arg.update({"type": self.type})
        self.arg_js = {}
        if "duration" in self.arg:
            self.arg_js["trial_duration"] = self.arg["duration"]
        for key in self.arg:
            self.arg_js[key] = args[key]
        # Per-instance copy so appending here never mutates the class-level
        # default and bleeds into other stimuli. See `excludes` for the
        # original (less-safe) class-attribute pattern we're not repeating.
        self.data_excludes: List[str] = []
        # Object literal emitted as `save_trial_parameters: {...}` in the
        # trial config. Lets us turn off jsPsych's automatic saving of
        # specific config fields (e.g. `stimulus`) into trial data without
        # removing the field from the trial config itself. See AUTHORING.md
        # §"Suppressing fields from trial data" and `skip_data`.
        self.save_trial_parameters: dict = {}

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

    def _on_load_js(self) -> str:
        # Always emit on_load so a transition from a fit=True to a fit=False
        # trial (e.g. instruction → consent) cleanly clears the prior zoom
        # and restores scrolling. The window guard makes the call harmless
        # if older sweetbean HTML preambles didn't define __sb_fit__.
        flag = "true" if getattr(self, "fit_to_viewport", True) else "false"
        body = f"if(window.__sb_fit__){{window.__sb_fit__({flag});}}"
        # Optional response gate: swallow keydowns at the document
        # capture phase for the first `min_rt` ms so jsPsych's plugin
        # listener never sees them. The capture phase fires *before* any
        # bubble-phase listener (which is what jsPsych's
        # `getKeyboardResponse` registers), so this works regardless of
        # which html-keyboard-response plugin version is loaded. We
        # allow the participant to still see / hear other DOM events
        # (mouse, focus, scroll) — only keyboard advance is blocked.
        #
        # Visual indicator: stimuli may mark answer/key UI with
        # `data-sb-min-rt-reveal`. Such elements stay hidden during the
        # gate and simply appear when responses become active. The
        # stimulus itself is never dimmed and no loading/progress bar is
        # shown.
        # See AUTHORING.md §"Minimum response time".
        min_rt = max(0, int(getattr(self, "min_rt", 0) or 0))
        if min_rt > 0:
            body += (
                f"var __sb_min_rt={min_rt};"
                "var __sb_reveal=[].slice.call("
                "document.querySelectorAll('[data-sb-min-rt-reveal]'));"
                "__sb_reveal.forEach(function(el){"
                "el.__sb_min_rt_pointer_events=el.style.pointerEvents;"
                "el.style.visibility='hidden';"
                "el.style.pointerEvents='none';"
                "});"
                # Keyboard blocker
                "var __sb_block=function(e){"
                "e.stopImmediatePropagation();e.preventDefault();"
                "};"
                "document.addEventListener('keydown',__sb_block,true);"
                "setTimeout(function(){"
                "document.removeEventListener('keydown',__sb_block,true);"
                "__sb_reveal.forEach(function(el){"
                "el.style.visibility='visible';"
                "el.style.pointerEvents=el.__sb_min_rt_pointer_events||'';"
                "});"
                "},__sb_min_rt);"
            )
        return f"on_load:()=>{{{body}}},"

    def to_js(self):
        self.js = ""
        self.js_data = ""
        self.js_before = ""
        self.js_body = ""
        self._params_to_js()
        self.js = (
            f"{{{self.js_body}{self.js_before}{self._save_trial_parameters_js()}"
            f"{self._on_load_js()}"
            f"on_finish:(data)=>{{{self.js_data}}}}}"
        )

    def to_js_for_image(self):
        self.js = ""
        self.js_data = ""
        self.js_before = ""
        self.js_body = ""
        self._params_to_js_from_prepared()
        self.js = (
            f"{{{self.js_body}{self.js_before}{self._save_trial_parameters_js()}"
            f"{self._on_load_js()}"
            f"on_finish:(data)=>{{{self.js_data}}}}}"
        )

    def _save_trial_parameters_js(self) -> str:
        """Emit `save_trial_parameters: {...}` as a real object literal.

        We do **not** route this through `_param_to_js` because that
        helper wraps every value in a `()=>{...}` getter. jsPsych's
        `save_trial_parameters` is a config field that must be a plain
        object literal — wrapping it in a function silently disables it.
        """
        params = getattr(self, "save_trial_parameters", None)
        if not params:
            return ""
        return f"save_trial_parameters:{to_js(params)},"

    def skip_data(self, *keys: str) -> "_BaseStimulus":
        """Drop one or more trial fields from the recorded observation.

        For each ``key``:

        * Skips the SweetBean-emitted ``data["bean_<key>"] = <key>``
          line in this stimulus's ``on_finish`` callback (no
          ``bean_<key>`` in the saved data).
        * Sets ``save_trial_parameters[key] = False`` so jsPsych's
          built-in trial-parameter recorder also drops the raw field
          (``stimulus``, ``choices``, etc.) from the saved data.

        The participant-facing trial config is untouched — this only
        controls what ends up in the per-trial data row that gets
        uploaded by online runners.

        Common use: long timelines on Firebase-backed runners where
        per-trial rendered HTML would otherwise blow past the
        Firestore 1 MB document limit. See AUTHORING.md §"Suppressing
        fields from trial data".

        Returns ``self`` for chaining.
        """
        for key in keys:
            if key not in self.data_excludes:
                self.data_excludes.append(key)
            self.save_trial_parameters[key] = False
        return self

    def _params_to_js(self):
        self.js_body += f'type: {self.arg["type"]},'
        for key in self.arg_js:
            self._param_to_js(key, self.arg_js[key])
        for key in self.arg:
            if key not in self.arg_js:
                self._param_to_js_arg(key, self.arg[key])
        self._add_extensions()
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

    def _add_extensions(self):
        if not self.extensions:
            return
        res = "["

        for extension in self.extensions:
            res += "{"
            if "type" in extension:
                res += f'type: {extension["type"]},'
            if "params" in extension:
                res += "params: "
            for param in extension["params"]:
                res += "{" + param + ':"' + f'{extension["params"][param]}' + '"}'
            res += "}"
        res += "],"
        self.js_body += "extensions:" + res

    def process_l(
        self,
        prompts,
        get_input,
        multi_turn,
        datum=None,
        response_open_token="<<",
        response_close_token=">>",
    ):
        prompts.append(self._get_prompt_l())
        prompt_response = self._get_response_prompt_l()
        s_data = {}
        data = self.l_args.copy()
        if prompt_response:
            prompt_response = prompt_response.replace("<<", response_open_token)
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
            prompts[-1] += f"{response}{response_close_token}"
        data.update(s_data)
        return data, prompts

    def _get_prompt_l(self):
        if self.l_template is None:
            raise Exception("No template or function set for getting prompt")
        return Template(self.l_template).render(self.l_args)

    @classmethod
    def set_prompt(cls, prompt_template: str):
        """
        Override the language prompt template for this stimulus class.
        """
        if "_default_prompt_template" not in cls.__dict__:
            cls._default_prompt_template = cls.l_template
        cls.l_template = prompt_template

    @classmethod
    def reset_prompt(cls):
        """
        Reset language prompt template to the original class default.
        """
        if "_default_prompt_template" in cls.__dict__:
            cls.l_template = cls._default_prompt_template

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
        if key not in getattr(self, "data_excludes", []):
            self.js_data += data

    def _param_to_js_arg(self, key, param):
        if key in getattr(self, "data_excludes", []):
            return
        _, data = _set_param_js(key, param)
        self.js_data += data

    def _set_side_effects(self):
        for se in self.side_effects:
            self.js_data += se.to_js()
            if not isinstance(se.set_variable, DataVariable):
                self.js_data += (
                    f'data["bean_{se.set_variable.name}"]={se.set_variable.name};'
                )

    def create_touch_layout(self):
        def get_touch_buttons(arg):
            buttons = set()

            def _collect(val):
                if isinstance(val, list):
                    for item in val:
                        _collect(item)

                elif isinstance(val, FunctionVariable):
                    for b in val.args:
                        _collect(b)

                    func = val.fct
                    code = func.__code__
                    global_vars = func.__globals__

                    # Check globals
                    for name in code.co_names:
                        if name in global_vars:
                            value = global_vars[name]
                            if isinstance(value, TouchButton):
                                buttons.add(value)

                    # Check closures
                    if func.__closure__ and code.co_freevars:
                        for name, cell in zip(code.co_freevars, func.__closure__):
                            value = cell.cell_contents
                            if isinstance(value, TouchButton):
                                buttons.add(value)

                    # NEW: Check for constructors inside the function body
                    buttons.update(collect_touch_buttons_from_function(func))

                elif isinstance(val, TouchButton):
                    buttons.add(val)

            _collect(arg)
            return list(buttons)

        if "choices" not in self.arg_js:
            return None
        else:
            maybe_list = get_touch_buttons(self.arg_js["choices"])
        layouts = []
        for key in maybe_list:
            if isinstance(key, TouchButton):
                layouts.append(key.layout)
        if not layouts:
            return None
        else:
            layout_name = f"layout_{uuid.uuid4().hex[:6]}"
            self.extensions = [
                {
                    "type": "jsPsychExtensionTouchscreenButtons",
                    "params": {"layout": layout_name},
                }
            ]

        return {layout_name: layouts}

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
    _default_response_template = response_template

    response_key = "response"

    def _process_response(self):
        self.js_data += f'data["bean_response"]=data["{self.response_key}"];'
        self.js_data += 'data["bean_rt"]=(typeof data["rt"]==="number")?data["rt"]:null;'
        self.js_data += (
            'if(!data["bean_correct_key"]){data["bean_correct"]=null;}'
            f'else{{data["bean_correct"]=data["bean_correct_key"]===data["{self.response_key}"];}}'
        )

    def _get_response_prompt_l(self):
        if not self.l_args["choices"]:
            return None
        return Template(self.response_template).render(
            {"choices": [c.upper() for c in self.l_args["choices"]]}
        )

    @classmethod
    def set_response_prompt(cls, response_template: str):
        """
        Override the response-prompt template for this stimulus class.
        """
        if "_default_response_template" not in cls.__dict__:
            cls._default_response_template = cls.response_template
        cls.response_template = response_template

    @classmethod
    def reset_response_prompt(cls):
        """
        Reset response-prompt template to the original class default.
        """
        if "_default_response_template" in cls.__dict__:
            cls.response_template = cls._default_response_template

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
