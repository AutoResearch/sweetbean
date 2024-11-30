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
        self.to_js()

    def to_js(self):
        self.js = ""
        for b in self.blocks:
            b.to_js()
            for s in b.stimuli:
                for key in s.arg:
                    if isinstance(s.arg[key], SharedVariable) or isinstance(
                        s.arg[key], CodeVariable
                    ):
                        self.js += f"{s.arg[key].set()}\n"
        self.js += "jsPsych = initJsPsych();\n"
        self.js += "trials = [\n"
        for b in self.blocks:
            self.js += b.js
            self.js += ","
        self.js = self.js[:-1] + "]\n"
        self.js += ";jsPsych.run(trials)"

    def to_html(self, path, local_save=True):
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
    ):
        data = []
        prompts = []
        for b in self.blocks:
            timeline = b.timeline
            stimuli = b.stimuli
            if not timeline:
                timeline = [{}]
            for timeline_element in timeline:
                data, prompts = run_stimuli(
                    stimuli, timeline_element, data, prompts, get_input
                )


def run_stimuli(stimuli, timeline_element, data, prompts, get_input):
    for s in stimuli:
        s_data = {}
        s.prepare_l_args(timeline_element, data)
        prompts.append(s.get_prompt())
        prompt_response = s.get_response_prompt()
        if prompt_response:
            prompts[-1] += " " + prompt_response
            response = get_input(" ".join([p for p in prompts])).upper()
            s_data.update(s.process_response(response))
            prompts[-1] += f"{response}>>"
        data.append(s_data)
        print(data)
    return data, prompts
