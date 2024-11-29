from typing import List

from sweetbean_v2._const import (
    FUNCTION_APPENDIX,
    FUNCTION_PREAMBLE,
    HTML_APPENDIX,
    HTML_PREAMBLE,
    TEXT_APPENDIX,
)
from sweetbean_v2.block import Block


class Experiment:
    blocks: List[Block] = []
    js = ""

    def __init__(self, blocks: List[Block]):
        self.blocks = blocks
        self.to_js()

    def to_js(self):
        self.js = "jsPsych = initJsPsych();\n"
        self.js += "trials = [\n"
        for b in self.blocks:
            self.js += b.js
            self.js += ","
        self.js = self.js[:-1] + "]\n"
        self.js += ";jsPsych.run(trials)"

    def to_html(self, path):
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


#
#     def run_on_language(
#             self,
#             get_input=input,
#             parse_response=lambda x, y: x == y,
#             multiturn=False,
#             intro="",
#             reaction_template="{{reaction}}>>.",
#             show_duaration=True,
#     ):
#         """
#         Run the experiment in language form.
#         Arguments:
#             get_input: a function that takes a stimulus and returns a response (could be a llm)
#             parse_response: a function that takes a response and returns the response
#         """
#         data_lst = {}
#         prompts_single = []
#         prompts_multiturn = []
#         full_chat = intro
#         current_prompt = ""
#
#         for b in self.blocks:
#             timeline = b.timeline
#             stimuli = b.stimuli
#             if timeline == []:
#                 timeline = [{}]
#
#             for timeline_element in timeline:
#                 (
#                     full_chat,
#                     current_prompt,
#                     data_lst,
#                     prompts_single,
#                     prompts_multiturn,
#                 ) = _run_stimuli(
#                     stimuli,
#                     timeline_element,
#                     full_chat,
#                     current_prompt,
#                     data_lst,
#                     prompts_single,
#                     prompts_multiturn,
#                     get_input,
#                     parse_response,
#                     multiturn,
#                     reaction_template,
#                     show_duaration,
#                 )
#         return {
#             "full_chat": full_chat,
#             "data_lst": data_lst,
#             "prompts_single": prompts_single,
#             "prompts_multiturn": prompts_multiturn,
#             "intro": intro,
#             "reaction_appendix": reaction_template,
#             "multiturn": multiturn,
#         }
#
#
# def _get_param(v_, timeline_element, data_list, window):
#     v_ = v_
#     if isinstance(v_, TimelineVariable):
#         v_ = timeline_element[v_.name]
#     if isinstance(v_, DataVariable):
#         if window < 1:
#             raise Exception("Window cannot be bellow 1")
#         v_ = data_list[v_.name][-1 - (window - 1)]
#     return v_
#
#
# def _get_param_w_d(v_, timeline_element, data_lst):
#     if isinstance(v_, DerivedParameter):
#         lvls = v_.levels
#         for lvl in lvls:
#             factors = [
#                 _get_param(f, timeline_element, data_lst, lvl.window)
#                 for f in lvl.factors
#             ]
#             if lvl.predicate(*factors):
#                 v_ = lvl.value
#     return v_
#
#
# def _run_stimuli(
#         stimuli,
#         timeline_element,
#         full_chat,
#         current_prompt,
#         data_lst,
#         prompts_single,
#         prompts_multiturn,
#         get_input=input,
#         parse_response=lambda x, y: x == y,
#         multiturn=False,
#         reaction_template="{{reaction}}>>.",
#         show_duration=True,
# ):
#     for s in stimuli:
#         data_stim = {}
#         for a, v in s.arg.items():
#             a_ = a
#             v_ = v
#             if isinstance(v_, TimelineVariable):
#                 v_ = timeline_element[v.name]
#             if isinstance(v_, DataVariable):
#                 if v_.window < 1:
#                     raise Exception("Window cannot be bellow 1")
#                 v_ = data_lst[v_.name][-1 - (v_.window - 1)]
#             if isinstance(v_, DerivedParameter):
#                 lvls = v_.levels
#                 for lvl in lvls:
#                     factors = [
#                         _get_param(f, timeline_element, data_lst, lvl.window)
#                         for f in lvl.factors
#                     ]
#                     if lvl.predicate(*factors):
#                         v_ = lvl.value
#             data_stim[a_] = v_
#
#         prompts_single += [s.show(show_duration, **data_stim)]
#         full_chat += s.show(**data_stim)
#         current_prompt += s.show(**data_stim)
#
#         for a, v in s.arg.items():
#             a_ = a
#             v_ = v
#             if isinstance(v_, TimelineVariable):
#                 v_ = timeline_element[v.name]
#             if isinstance(v_, DerivedParameter):
#                 lvls = v_.levels
#                 for lvl in lvls:
#                     factors = [
#                         _get_param(f, timeline_element, data_lst, lvl.window)
#                         for f in lvl.factors
#                     ]
#                     if lvl.predicate(*factors):
#                         v_ = lvl.value
#             if a_ == "choices" and v_:
#                 if multiturn:
#                     reaction = get_input(current_prompt)
#                 else:
#                     reaction = get_input(full_chat)
#                 prompts_multiturn += [prompts_multiturn]
#                 prompts_single += reaction
#                 full_chat += Template(reaction_template).render({"reaction": reaction})
#                 current_prompt = reaction
#                 data_stim["response"] = reaction
#                 correct = None
#                 if "correct_key" in s.arg:
#                     correct = parse_response(
#                         reaction,
#                         _get_param_w_d(
#                             s.arg["correct_key"], timeline_element, data_lst
#                         ),
#                     )
#                 data_stim["correct"] = correct
#         m = 0
#         for k, v in data_lst.items():
#             if len(v) > m:
#                 m = len(v)
#
#         for key in data_lst.keys() | data_stim.keys():
#             if key in data_lst and key in data_stim:
#                 data_lst[key].append(data_stim[key])
#             elif key in data_lst:
#                 data_lst[key].append(None)
#             else:
#                 data_lst[key] = [None] * m + [data_stim[key]]
#
#     return full_chat, current_prompt, data_lst, prompts_single, prompts_multiturn
