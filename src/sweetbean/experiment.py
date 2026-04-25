import re
from typing import Any, List

from sweetbean._const import (
    FUNCTION_APPENDIX,
    FUNCTION_PREAMBLE,
    HTML_APPENDIX,
    HTML_PREAMBLE,
    TEXT_APPENDIX,
)
from sweetbean.block import Block
from sweetbean.variable import CodeVariable

# Injected by :meth:`Experiment.compile`, replaced in :meth:`Experiment.to_js_string_from_template`.
_TIMELINE_PLACEHOLDER_RE = re.compile(r"__SB_TIMELINE_PLACEHOLDER_(\d+)__")


def _timeline_placeholder(block_index: int) -> str:
    return f"__SB_TIMELINE_PLACEHOLDER_{block_index}__"


class Experiment:
    """
    An experiment consisting of blocks
    """

    blocks: List[Block] = []
    js = ""

    def __init__(self, blocks: List[Block], protections=None):
        """
        Arguments:
            blocks: a list of blocks
            protections: optional list of :class:`sweetbean.protection.Protection`
                instances. Each protection embeds its own JS into the compiled
                experiment at well-defined hook points (head, runtime, init,
                per-trial on_load/on_finish, summary). See
                :mod:`sweetbean.protection` for the contract.
        """
        self.blocks = blocks
        self.protections = list(protections) if protections else []

    def _protection_head_assets(self) -> str:
        return "".join(p.head_assets() for p in self.protections if p.head_assets())

    def _protection_runtime_js(self) -> str:
        parts = [p.runtime_js() for p in self.protections]
        return "\n".join(part for part in parts if part)

    def _protection_init_js(self) -> str:
        parts = [p.init_js() for p in self.protections]
        return "\n".join(part for part in parts if part)

    def _protection_summary_js(self) -> str:
        """JS statement that adds each protection's summary onto every saved
        trial row via ``jsPsych.data.addProperties``. Empty if no protection
        emits a summary."""
        entries = []
        for p in self.protections:
            expr = p.summary_js()
            if expr:
                entries.append(f"{p.name}:{expr}")
        if not entries:
            return ""
        return "jsPsych.data.addProperties({" + ",".join(entries) + "});"

    def to_js(self, path_local_download=None):
        from sweetbean.protection._context import set_active_protections

        self.js = ""
        shared_variables = {}
        extensions = ""
        # Protection runtime libs go FIRST so window.<Lib> is in scope by the
        # time anything else runs. Active-protections context is set BEFORE
        # block.to_js so per-trial hooks (on_load/on_finish) are emitted.
        runtime = self._protection_runtime_js()
        if runtime:
            self.js += runtime + "\n"
        set_active_protections(self.protections)
        try:
            for b in self.blocks:
                b.to_js()
                extensions += _initialize_extensions(b.extensions)
                for s in b.stimuli:
                    shared_variables.update(s.return_shared_variables())
            for s_key in shared_variables:
                self.js += f"{shared_variables[s_key].set()}\n"
            summary = self._protection_summary_js()
            init = self._protection_init_js()
            if path_local_download:
                if path_local_download.endswith(".json"):
                    save_call = (
                        f"jsPsych.data.get().localSave('json',"
                        f"'{path_local_download}')"
                    )
                elif path_local_download.endswith(".csv"):
                    save_call = (
                        f"jsPsych.data.get().localSave('csv',"
                        f"'{path_local_download}')"
                    )
                else:
                    raise Exception(
                        "Unknown file format for local download. "
                        "Only .json or .csv are supported."
                    )
                on_finish_body = f"{summary}{save_call}"
                opts = f"{{on_finish:()=>{{{on_finish_body}}}}}"
                if extensions == "":
                    self.js += f"jsPsych = initJsPsych({opts});\n"
                else:
                    self.js += f"jsPsych = initJsPsych({extensions}{opts});\n"
            elif summary:
                opts = f"{{on_finish:()=>{{{summary}}}}}"
                if extensions == "":
                    self.js += f"jsPsych = initJsPsych({opts});\n"
                else:
                    self.js += f"jsPsych = initJsPsych({extensions}{opts});\n"
            else:
                self.js += f"jsPsych = initJsPsych({extensions});\n"
            if init:
                self.js += init + "\n"
            self.js += "trials = [\n"
            for b in self.blocks:
                self.js += b.js
                self.js += ","
            self.js = self.js[:-1] + "]\n"
            self.js += ";jsPsych.run(trials)"
        finally:
            set_active_protections([])

    def to_html(self, path, path_local_download=None):
        """
        Save the experiment to an HTML file
        """
        self.to_js(path_local_download)
        # Protection head_assets() (extra <link>/<script> tags) are emitted
        # right after the preamble's opening <script>; runtime_js (e.g. the
        # inlined BotDetection IIFE) is already part of self.js, prepended
        # in to_js so it executes before initJsPsych.
        head_assets = self._protection_head_assets()
        html = HTML_PREAMBLE
        if head_assets:
            html += "</script>\n" + head_assets + "<script>\n"
        html += f"{self.js}" + HTML_APPENDIX

        with open(path, "w") as f:
            f.write(html)

    def to_js_string(self, as_function=True, is_async=True):
        """
        Return the experiment as a JavaScript string
        """
        from sweetbean.protection._context import set_active_protections

        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        runtime = self._protection_runtime_js()
        if runtime:
            text += runtime + "\n"
        extensions = ""
        set_active_protections(self.protections)
        try:
            for b in self.blocks:
                b.to_js()
                extensions += _initialize_extensions(b.extensions)
                for s in b.stimuli:
                    shared_variables = s.return_shared_variables()
                    for s_key in shared_variables:
                        text += f"{shared_variables[s_key].set()}\n"
            text += f"const jsPsych = initJsPsych({extensions})\n"
            init = self._protection_init_js()
            if init:
                text += init + "\n"
            text += "const trials = [\n"
            for b in self.blocks:
                text += b.js
                text += ","
            text = text[:-1] + "]\n"
        finally:
            set_active_protections([])
        # Summary lands on every saved row by running addProperties AFTER
        # jsPsych.run completes — that's why it goes into post_run_js, not
        # initJsPsych's on_finish (which would race with the run loop in
        # the function-style output).
        post_run = self._protection_summary_js()
        if as_function:
            text += FUNCTION_APPENDIX(is_async, post_run)
        else:
            text += TEXT_APPENDIX(is_async, post_run)
        return text

    def compile(self, as_function=True, is_async=True):
        """
        Build JavaScript once: stimulus graphs and ``jsPsych`` setup are emitted;
        each block's ``timeline_variables`` is a placeholder string that
        :meth:`to_js_string_from_template` replaces with per-condition data.

        Use when multiple conditions share the same stimulus structure (e.g. Firebase
        payloads) so timelines are "injected" without re-running Transcrypt per condition.
        """
        from sweetbean.protection._context import set_active_protections

        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        runtime = self._protection_runtime_js()
        if runtime:
            text += runtime + "\n"
        extensions = ""
        set_active_protections(self.protections)
        try:
            for bi, b in enumerate(self.blocks):
                if isinstance(b.timeline, CodeVariable):
                    b.to_js()
                else:
                    b.to_js(template_timeline_token=_timeline_placeholder(bi))
                extensions += _initialize_extensions(b.extensions)
                for s in b.stimuli:
                    shared_variables = s.return_shared_variables()
                    for s_key in shared_variables:
                        text += f"{shared_variables[s_key].set()}\n"
            text += f"const jsPsych = initJsPsych({extensions})\n"
            init = self._protection_init_js()
            if init:
                text += init + "\n"
            text += "const trials = [\n"
            for b in self.blocks:
                text += b.js
                text += ","
            text = text[:-1] + "]\n"
        finally:
            set_active_protections([])
        post_run = self._protection_summary_js()
        if as_function:
            text += FUNCTION_APPENDIX(is_async, post_run)
        else:
            text += TEXT_APPENDIX(is_async, post_run)
        return text

    @staticmethod
    def to_js_string_from_template(template: str, timelines: List[Any]) -> str:
        """
        Replace each ``__SB_TIMELINE_PLACEHOLDER_i__`` in *template* with the JS literal
        for ``timelines[i]`` (from :func:`sweetbean.util.parse.to_js`).

        *timelines* must have one entry per block that used a placeholder in
        :meth:`compile` (same order as ``Experiment.blocks``). Blocks compiled with
        :class:`~sweetbean.variable.CodeVariable` timelines embed real JS and are not
        listed here — pass the full list of block timelines, including those unchanged.
        """
        from sweetbean.util.parse import to_js as sb_to_js

        def _repl(m: re.Match) -> str:
            idx = int(m.group(1))
            if idx < 0 or idx >= len(timelines):
                raise ValueError(
                    f"Template references timeline placeholder {idx}; "
                    f"got {len(timelines)} timeline(s)"
                )
            return sb_to_js(timelines[idx])

        return _TIMELINE_PLACEHOLDER_RE.sub(_repl, template)

    def run_on_language(
        self,
        get_input=input,
        multi_turn=False,
        preamble="",
        data=None,
        response_open_token="<<",
        response_close_token=">>",
    ):
        """
        Run the experiment in a language

        Arguments:
            get_input: a function to get input from the response
                (for example, a function that prompts language model and returns the response)
            multi_turn: a boolean to allow multi-turn input.
                If True, the prompts are not concatenated.
            preamble: a string to be added before the prompts
            data: a list of dictionaries with the data.
                This will rerun the experiment with the data as input.
                If the data is not provided for the full experiment,
                the rest of it will be simulated with the get_input function.
            response_open_token: token used in prompt templates for "answer starts here".
            response_close_token: token appended after model/user answer in stored prompts.
        """
        out_data = []
        prompts = []
        shared_variables = {}
        for b in self.blocks:
            for s in b.stimuli:
                _shared_variables = s.return_shared_variables()
                for s_key in _shared_variables:
                    shared_variables[s_key] = _shared_variables[s_key].value
        datum_index = 0
        for b in self.blocks:
            timeline = b.timeline
            stimuli = b.stimuli
            if not timeline:
                timeline = [{}]
            for timeline_element in timeline:
                out_data, prompts, shared_variables, datum_index = run_stimuli(
                    stimuli,
                    timeline_element,
                    out_data,
                    shared_variables,
                    prompts,
                    get_input,
                    multi_turn,
                    datum_index,
                    data,
                    preamble,
                    response_open_token,
                    response_close_token,
                )
        return out_data, prompts


def run_stimuli(
    stimuli,
    timeline_element,
    out_data,
    shared_variables,
    prompts,
    get_input,
    multi_turn,
    datum_index,
    data,
    preamble,
    response_open_token,
    response_close_token,
):
    for s in stimuli:
        if data and datum_index < len(data):
            datum = data[datum_index]
        else:
            datum = None
        s._prepare_args_l(timeline_element, out_data, shared_variables, datum)

        def _get_input(_prompt):
            if not preamble:
                return get_input(_prompt)
            else:
                return get_input(f"{preamble} {_prompt}")

        s_out_data, prompts = s.process_l(
            prompts,
            _get_input,
            multi_turn,
            datum,
            response_open_token=response_open_token,
            response_close_token=response_close_token,
        )
        out_data.append(s_out_data)
        if s.side_effects:
            s._resolve_side_effects(timeline_element, out_data, shared_variables)
            shared_variables.update(s.l_ses)
            _d = {}
            for key in s.l_ses:
                if key.startswith('data["bean_') or key.startswith("data['bean_"):
                    _d[key[11:-2]] = s.l_ses[key]
                else:
                    _d[key] = s.l_ses[key]
            out_data[-1].update(_d)
        datum_index += 1
    return out_data, prompts, shared_variables, datum_index


def _initialize_extensions(extensions):
    all = ""
    t_l = ""
    if (
        "touch_layouts" in extensions
        and len(extensions["touch_layouts"]) > 0
        and any(extensions["touch_layouts"])
    ):
        t_l += "{type: jsPsychExtensionTouchscreenButtons, params: {"
        for touch_layout in extensions["touch_layouts"]:
            if not touch_layout:
                continue
            for key, item in touch_layout.items():
                t_l += f"{key}"
                t_l += ":["
                _v = ""
                if item:
                    for _k in item:
                        _v += "{key:"
                        _v += f'"{_k["key"]}"'
                        if "color" in _k:
                            _v += f',color: "{_k["color"]}"'
                        if "preset" in _k:
                            _v += f',preset: "{_k["preset"]}"'
                        _v += "},"
                if _v:
                    _v = _v[:-1]
                t_l += _v
                t_l += "],"
            t_l = t_l[:-1]
            if t_l:
                t_l += "}"
    if t_l:
        all = "{extensions: [" + t_l + "}]},"

    return all
