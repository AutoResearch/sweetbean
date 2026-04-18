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

    def __init__(self, blocks: List[Block]):
        """
        Arguments:
            blocks: a list of blocks
        """
        self.blocks = blocks

    def to_js(self, path_local_download=None):
        self.js = ""
        shared_variables = {}
        extensions = ""
        for b in self.blocks:
            b.to_js()
            extensions += _initialize_extensions(b.extensions)
            for s in b.stimuli:
                shared_variables.update(s.return_shared_variables())
        for s_key in shared_variables:
            self.js += f"{shared_variables[s_key].set()}\n"
        if path_local_download:
            if path_local_download.endswith(".json"):
                if extensions == "":
                    self.js += "jsPsych = initJsPsych("
                else:
                    self.js += f"jsPsych = initJsPsych({extensions},"
                self.js += (
                    f"{{on_finish:()=>jsPsych.data.get().localSave('json',"
                    f"'{path_local_download}')}});\n"
                )
            elif path_local_download.endswith(".csv"):
                if extensions == "":
                    self.js += "jsPsych = initJsPsych("
                else:
                    self.js += f"jsPsych = initJsPsych({extensions},"
                self.js += (
                    f"{{on_finish:()=>jsPsych.data.get().localSave('csv',"
                    f"'{path_local_download}')}});\n"
                )
            else:
                raise Exception(
                    "Unknown file format for local download. "
                    "Only .json or .csv are supported."
                )
        else:
            self.js += f"jsPsych = initJsPsych({extensions});\n"
        self.js += "trials = [\n"
        for b in self.blocks:
            self.js += b.js
            self.js += ","
        self.js = self.js[:-1] + "]\n"
        self.js += ";jsPsych.run(trials)"

    def to_html(self, path, path_local_download=None):
        """
        Save the experiment to an HTML file
        """
        self.to_js(path_local_download)
        html = HTML_PREAMBLE
        blocks = 0

        if blocks > 0:
            html += "</script><script>\n"
        html += f"{self.js}" + HTML_APPENDIX

        with open(path, "w") as f:
            f.write(html)

    def to_js_string(self, as_function=True, is_async=True):
        """
        Return the experiment as a JavaScript string
        """
        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        extensions = ""
        for b in self.blocks:
            b.to_js()
            extensions += _initialize_extensions(b.extensions)
            for s in b.stimuli:

                shared_variables = s.return_shared_variables()
                for s_key in shared_variables:
                    text += f"{shared_variables[s_key].set()}\n"
        text += f"const jsPsych = initJsPsych({extensions})\n"
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.js
            text += ","
        text = text[:-1] + "]\n"
        text += FUNCTION_APPENDIX(is_async) if as_function else TEXT_APPENDIX(is_async)
        return text

    def compile(self, as_function=True, is_async=True):
        """
        Build JavaScript once: stimulus graphs and ``jsPsych`` setup are emitted;
        each block's ``timeline_variables`` is a placeholder string that
        :meth:`to_js_string_from_template` replaces with per-condition data.

        Use when multiple conditions share the same stimulus structure (e.g. Firebase
        payloads) so timelines are "injected" without re-running Transcrypt per condition.
        """
        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        extensions = ""
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
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.js
            text += ","
        text = text[:-1] + "]\n"
        text += FUNCTION_APPENDIX(is_async) if as_function else TEXT_APPENDIX(is_async)
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
