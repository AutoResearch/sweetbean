from typing import List

from sweetbean._const import (
    FUNCTION_APPENDIX,
    FUNCTION_PREAMBLE,
    HTML_APPENDIX,
    HTML_PREAMBLE,
    TEXT_APPENDIX,
)
from sweetbean.block import Block
from sweetbean.variable import CodeVariable, SharedVariable


class Experiment:
    blocks: List[Block] = []
    js = ""

    def __init__(self, blocks: List[Block]):
        self.blocks = blocks

    def to_js(self, path_local_download=None):
        self.js = ""
        for b in self.blocks:
            b.to_js()
            for s in b.stimuli:
                for key in s.arg:
                    if isinstance(s.arg[key], SharedVariable) or isinstance(
                        s.arg[key], CodeVariable
                    ):
                        self.js += f"{s.arg[key].set()}\n"
        if path_local_download:
            self.js += (
                "jsPsych = initJsPsych("
                f"{{on_finish:()=>jsPsych.data.get().localSave('json',"
                f"'{path_local_download}')}});\n"
            )
        else:
            self.js += "jsPsych = initJsPsych();\n"
        self.js += "trials = [\n"
        for b in self.blocks:
            self.js += b.js
            self.js += ","
        self.js = self.js[:-1] + "]\n"
        self.js += ";jsPsych.run(trials)"

    def to_html(self, path, path_local_download=None):
        self.to_js(path_local_download)
        html = HTML_PREAMBLE
        blocks = 0

        if blocks > 0:
            html += "</script><script>\n"
        html += f"{self.js}" + HTML_APPENDIX

        with open(path, "w") as f:
            f.write(html)

    def to_js_string(self, as_function=True, is_async=True):
        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        text += "const jsPsych = initJsPsych()\n"
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.js
            text += ","
        text = text[:-1] + "]\n"
        text += FUNCTION_APPENDIX(is_async) if as_function else TEXT_APPENDIX(is_async)
        return text

    def run_on_language(
        self,
        get_input=input,
        multi_turn=False,
    ):
        data = []
        prompts = []
        shared_variables = {}
        for b in self.blocks:
            for s in b.stimuli:
                for key in s.arg:
                    if isinstance(s.arg[key], SharedVariable) or isinstance(
                        s.arg[key], CodeVariable
                    ):
                        shared_variables[s.arg[key].name] = s.arg[key].value
        for b in self.blocks:
            timeline = b.timeline
            stimuli = b.stimuli
            if not timeline:
                timeline = [{}]
            for timeline_element in timeline:
                data, prompts, shared_variables = run_stimuli(
                    stimuli,
                    timeline_element,
                    data,
                    shared_variables,
                    prompts,
                    get_input,
                    multi_turn,
                )
        return data, prompts


def run_stimuli(
    stimuli, timeline_element, data, shared_variables, prompts, get_input, multi_turn
):
    for s in stimuli:
        s._prepare_args_l(timeline_element, data, shared_variables)
        s_data, prompts = s.process_l(prompts, get_input, multi_turn)
        data.append(s_data)
        if s.side_effects:
            s._resolve_side_effects(timeline_element, data, shared_variables)
            shared_variables.update(s.l_ses)
    return data, prompts, shared_variables
