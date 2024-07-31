import itertools
from typing import Callable, List


def param_to_psych(param):
    if isinstance(param, List):
        return param
    elif getattr(param, "text_js", None):
        return param.text_js
    elif isinstance(param, bool):
        if param:
            return "true"
        else:
            return "false"
    elif isinstance(param, int):
        return param
    else:
        param = str(param)
        if param.startswith('"') and param.endswith('"'):
            return param
        else:
            return f'"{param}"'


def level_to_data(param, i):
    if getattr(param, "name", None):
        return f'jsPsych.data.get().last({i})["trials"][0]["bean_{param.name}"]'
    return f'jsPsych.data.get().last({i})["trials"][0]["bean_{param}"]'


class TimelineVariable:
    name: str = ""
    text_js = ""

    def __init__(self, name, levels=[]):
        self.name = str(name)
        self.levels = levels
        self.to_psych()

    def to_psych(self):
        self.text_js = f"jsPsych.timelineVariable('{self.name}')"


class DataVariable:
    name: str = ""
    text_js = ""

    def __init__(self, name, levels=[]):
        self.name = str(name)
        self.levels = levels

    def to_psych(self):
        self.text_js = self.name


class CodeVariable:
    name: str = ""
    text_js = ""

    def __init__(self, name, levels=[]):
        self.name = str(name)
        self.levels = levels

    def to_psych(self):
        self.text_js = self.name


class CorrectDataVariable(DataVariable):
    def __init__(self):
        super().__init__("correct", [True, False])


class DerivedLevel:
    value: str
    predicate: Callable
    factors: List[TimelineVariable]
    text_js = ""
    cond_js = ""
    window = 0

    def __init__(self, value, predicate, factors, window=0):
        self.value = value
        self.predicate = predicate
        self.factors = factors
        self.window = window
        self.to_psych()

    def to_psych(self):
        self.text_js = self.value
        level_list = [f.levels for f in self.factors]
        for i in range(len(level_list)):
            for j in range(len(level_list[i])):
                if not isinstance(level_list[i][j], bool):
                    level_list[i][j] = param_to_psych(level_list[i][j]).replace('"', "")
        level_combination = list(itertools.product(*level_list))
        js_string = ""
        for comb in level_combination:
            arg = [f for f in comb]
            if self.predicate(*arg):
                js_string += "("
                for i in range(len(comb)):
                    left_side = param_to_psych(self.factors[i])
                    if left_side.startswith("()"):
                        left_side = f"({left_side})()"
                    if self.window > 0:
                        left_side = level_to_data(self.factors[i], self.window)
                    right_side = param_to_psych(arg[i])
                    if right_side == '"true"' or right_side == '"false"':
                        right_side = right_side[1:-1]
                    if right_side.startswith("()"):
                        right_side = f"({right_side})()"
                    js_string += f"{left_side} === {right_side}"
                    if i < len(comb) - 1:
                        js_string += " && "
                    else:
                        js_string += ") || "
        if js_string == "":
            return ""
        self.cond_js = js_string[:-4]


class DerivedParameter:
    name: str
    levels: List[DerivedLevel]
    text_js = ""

    def __init__(self, name, levels):
        self.name = name
        self.levels = levels
        self.to_psych()

    def to_psych(self):
        js_string = "() => {"
        for lvl in self.levels:
            js_string += f"if ({lvl.cond_js})"
            js_string += "{"
            js_string += f"return {param_to_psych(lvl.value)}"
            js_string += "}"
        js_string += "}"
        self.text_js = js_string
