from typing import List

from sweetbean._const import (
    FUNCTION_APPENDIX,
    FUNCTION_PREAMBLE,
    HTML_APPENDIX,
    HTML_PREAMBLE,
    TEXT_APPENDIX,
)
from sweetbean.block import Block


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
        for b in self.blocks:
            b.to_js()
            for s in b.stimuli:
                shared_variables.update(s.return_shared_variables())
        for s_key in shared_variables:
            self.js += f"{shared_variables[s_key].set()}\n"
        if path_local_download:
            if path_local_download.endswith(".json"):
                self.js += (
                    "jsPsych = initJsPsych("
                    f"{{on_finish:()=>jsPsych.data.get().localSave('json',"
                    f"'{path_local_download}')}});\n"
                )
            elif path_local_download.endswith(".csv"):
                self.js += (
                    "jsPsych = initJsPsych("
                    f"{{on_finish:()=>jsPsych.data.get().localSave('csv',"
                    f"'{path_local_download}')}});\n"
                )
            else:
                raise Exception(
                    "Unknown file format for local download. "
                    "Only .json or .csv are supported."
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
        for b in self.blocks:
            b.to_js()
            for s in b.stimuli:
                shared_variables = s.return_shared_variables()
                for s_key in shared_variables:
                    text += f"{shared_variables[s_key].set()}\n"
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
        preamble="",
        data=None,
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
):
    for s in stimuli:
        if data and datum_index < len(data):
            datum = data[datum_index]
        else:
            datum = None
        s._prepare_args_l(timeline_element, out_data, shared_variables, datum)

        def _get_input(_prompt):
            if not multi_turn or not preamble:
                return get_input(_prompt)
            else:
                return get_input(f"{preamble} {_prompt}")

        s_out_data, prompts = s.process_l(prompts, _get_input, multi_turn, datum)
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
