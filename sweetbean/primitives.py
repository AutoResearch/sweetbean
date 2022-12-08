from __future__ import annotations
from typing import List, Callable
import itertools


class TimelineVariable:
    name: str = ''

    def __init__(self, name, levels=[]):
        self.name = str(name)
        self.levels = levels

    def to_psych(self):
        return f"jsPsych.timelineVariable('{self.name}')"


def _param_to_psych(param):
    if isinstance(param, List):
        return param
    elif isinstance(param, TimelineVariable) or isinstance(param, DerivedParameter):
        return param.to_psych()
    elif isinstance(param, bool):
        if param:
            return 'true'
        else:
            return 'false'
    else:
        return '"' + str(param) + '"'


class Stimulus:
    """
    A Template for other Stimuli
    """
    type: str = None
    duration: int = 0
    sequence_splicers: List = []

    def __init__(self, *args):
        self.sequence_splicers = []
        for a in args:
            if isinstance(a, DerivedParameter):
                self.sequence_splicers.append(a)

    def to_psych(self):
        return ''


class TextStimulus(Stimulus):
    type = 'jsPsychHtmlKeyboardResponse'
    text: str = ''
    color: str = 'white'
    choices: List = []
    correct: str = ''

    def __init__(self, duration=None, text='', color='white', choices=[], correct=''):
        self.text = _param_to_psych(text)
        self.color = _param_to_psych(color)
        self.choices = _param_to_psych(choices)
        self.correct = _param_to_psych(correct)
        self.duration = _param_to_psych(duration)
        super(TextStimulus, self).__init__(text, color, choices, correct, duration)

    def to_psych(self):
        res = '{'
        res += f'type: {self.type},'
        res += f'trial_duration: {self.duration},'
        res += 'stimulus: () => {'
        res += f'let color = {self.color};'
        res += f'let text = {self.text};'
        res += 'return '
        res += '"<div style='
        res += "'"
        res += 'color: " + '
        res += 'color'
        if self.color.startswith('()'):
            res += '()'
        res += ' + "\'>" +'
        res += 'text'
        if self.text.startswith('()'):
            res += '()'
        res += " + '</div>'"
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct and self.correct != '""':
            res += ',on_finish: (data) => {'
            res += f'let correct = {self.correct}'
            res += f'data["correct"] = correct'
            if self.correct.startswith('()'):
                res += '()'
            res += '== data["response"]'
            res += '}'
        res += '}'
        return res


class SymbolStimulus(Stimulus):
    type = 'jsPsychHtmlKeyboardResponse'

    def __init__(self, duration=None, symbol='square', color='white', choices=[], correct=''):
        self.symbol = _param_to_psych(symbol)
        self.color = _param_to_psych(color)
        self.choices = _param_to_psych(choices)
        self.correct = _param_to_psych(correct)
        self.duration = _param_to_psych(duration)
        super(SymbolStimulus, self).__init__(symbol, color, choices, correct, duration)

    def to_psych(self):
        res = '{'
        res += f'type: {self.type},'
        res += f'trial_duration: {self.duration},'
        res += 'stimulus: () => { '
        res += f'let symbol = {self.symbol};'
        res += f'let color = {self.color};'
        res += f'let symbol_class = symbol'
        if self.symbol.startswith("()"):
            res += '()'
        res += ';'
        res += 'let c = "sweetbean-"+symbol_class;'
        res += 'return '
        res += f'"<div class=\'" + c + "\' style=" + '
        res += '"\'background: " + ('
        res += 'symbol'
        if self.symbol.startswith("()"):
            res += '()'
        res += ' == "triangle" ? "transparent" : '
        res += 'color'
        if self.color.startswith('()'):
            res += '()'
        res += ')'
        res += ' + ('
        res += 'symbol'
        if self.symbol.startswith('()'):
            res += '()'
        res += '== "triangle" ? "; border-bottom: solid 10vw " + '
        res += 'color'
        if self.color.startswith('()'):
            res += "()"
        res += ' : "") '
        res += ' + "\'></div>"'
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct and self.correct != '""':
            res += ',on_finish: (data) => {'
            res += f'let correct = {self.correct}'
            res += f'data["correct"] = correct'
            if self.correct.startswith('()'):
                res += '()'
            res += '== data["response"]'
            res += '}'
        res += '}'
        return res


class FlankerStimulus(Stimulus):
    type = 'jsPsychHtmlKeyboardResponse'

    def __init__(self, duration=None, direction='left', distractor='left', color='white', choices=[], correct=''):
        self.direction = _param_to_psych(direction)
        self.distractor = _param_to_psych(distractor)
        self.color = _param_to_psych(color)
        self.choices = _param_to_psych(choices)
        self.correct = _param_to_psych(correct)
        self.duration = _param_to_psych(duration)
        super(FlankerStimulus, self).__init__(direction, distractor, color, choices, correct, duration)

    def to_psych(self):
        res = '{' \
              f'type: {self.type},' \
              f'trial_duration: {self.duration},' \
              'stimulus: () => { return '
        res += '"<div style='
        res += "'"
        res += 'color: " + '
        res += self.color
        res += ' + "\'>" +'
        res += '(' + self.distractor + ' == "left" ? "< <" : "> >") +'
        res += '(' + self.direction + ' == "left" ? " < " : " > ")  +'
        res += '(' + self.distractor + ' == "left" ? "< <" : "> >")'
        res += " + '</div>'"
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct and self.correct != '""':
            res += ',on_finish: (data) => {'
            res += f'let correct = {self.correct}'
            res += f'data["correct"] = correct'
            if self.correct.startswith('()'):
                res += '()'
            res += '== data["response"]'
            res += '}'
        res += '}'
        return res


class FixationStimulus(Stimulus):
    def __init__(self, duration=None):
        self.duration = _param_to_psych(duration)
        super(FixationStimulus, self).__init__(duration)

    def to_psych(self):
        res = '{'
        res += 'type: jsPsychHtmlKeyboardResponse,'
        res += f'trial_duration: {self.duration},'
        res += 'stimulus: "<div>+</div>",'
        res += 'response_ends_trial: false'
        res += '}'
        return res


class BlankStimulus(Stimulus):
    def __init__(self, duration=None, choices=[], correct=''):
        self.duration = _param_to_psych(duration)
        self.choices = _param_to_psych(choices)
        self.correct = _param_to_psych(correct)
        super(BlankStimulus, self).__init__(duration, choices, correct)

    def to_psych(self):
        res = '{'
        res += 'type: jsPsychHtmlKeyboardResponse,'
        res += f'trial_duration: {self.duration},'
        res += 'stimulus: "",'
        res += f'choices: {self.choices}'
        if self.correct and self.correct != '""':
            res += ',on_finish: (data) => {'
            res += f'let correct = {self.correct}'
            res += f'data["correct"] = correct'
            if self.correct.startswith('()'):
                res += '()'
            res += '== data["response"]'
            res += '}'
        res += '}'
        return res


class FeedbackStimulus(Stimulus):
    def __init__(self, duration: int = None, kind: str = 'message', on_correct: bool = True):
        self.duration = _param_to_psych(duration)
        self.kind = _param_to_psych(kind)
        self.on_correct = _param_to_psych(on_correct)
        super(FeedbackStimulus, self).__init__(duration, kind, on_correct)

    def to_psych(self):
        res = '{'
        res += 'type: jsPsychHtmlKeyboardResponse,'
        res += 'trial_duration: () => {'
        res += 'let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;'
        res += 'if ((' + self.on_correct + '&& last_trial_correct) || !last_trial_correct) {'
        res += 'return ' + self.duration
        res += '} else {'
        res += 'return 0'
        res += '}},'
        res += 'stimulus: () => {'
        res += 'let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;'
        res += 'if (last_trial_correct) {'
        res += 'if (' + self.on_correct + '){'
        res += 'if (' + self.kind + ' == "message"){'
        res += 'return "<div class=' + "'feedback'" + '>Correct!</div>";'
        res += '} else if (' + self.kind + ' == "screen"){'
        res += 'return "<div class=\'feedback-screen-green\'></div>";'
        res += '}} else {'
        res += 'return ""}'
        res += '} else {'
        res += 'let last_trial_response = jsPsych.data.get().last(1).values()[0].response;'
        res += 'if (last_trial_response) {'
        res += 'if (' + self.kind + ' == "message"){'
        res += 'return "<div class=' + "'feedback'" + '>Wrong!</div>";'
        res += '} else if (' + self.kind + ' == "screen"){'
        res += 'return "<div class=\'feedback-screen-red\'></div>";'
        res += '}} else {'
        res += 'if (' + self.kind + ' == "message"){'
        res += 'return "<div class=' + "'feedback'" + '>Too slow!</div>";'
        res += '} else if (' + self.kind + ' == "screen"){'
        res += 'return "<div class=\'feedback-screen-red\'></div>";'
        res += '}}'
        res += '}'
        res += '},'
        res += 'response_ends_trial: false'
        res += '}'
        return res


class TrialSequence:
    def __init__(self, sequence):
        self.sequence = sequence

    def to_psych(self):
        return f'{str(self.sequence)}'


class DerivedLevel:
    value: str
    predicate: Callable
    factors: List[TimelineVariable]

    def __init__(self, value, predicate, factors):
        self.value = value
        self.predicate = predicate
        self.factors = factors

    def to_psych(self):
        level_list = [f.levels for f in self.factors]
        level_combination = list(itertools.product(*level_list))
        js_string = ''
        for comb in level_combination:
            arg = [f for f in comb]
            if self.predicate(*arg):
                js_string += '('
                for i in range(len(comb)):
                    js_string += f'{self.factors[i].to_psych()} === {_param_to_psych(arg[i])}'
                    if i < len(comb) - 1:
                        js_string += ' && '
                    else:
                        js_string += ') || '
        if js_string == '':
            return ''
        return js_string[:-4]


class DerivedParameter:
    name: str
    levels: List[DerivedLevel]

    def __init__(self, name, levels):
        self.name = name
        self.levels = levels

    def to_psych(self):
        js_string = '() => {'
        for l in self.levels:
            js_string += f'if ({l.to_psych()})'
            js_string += '{'
            js_string += f'return {_param_to_psych(l.value)}'
            js_string += '}'
        js_string += '}'
        return js_string


if __name__ == '__main__':
    train_sequence = TrialSequence(
        [{'task': 'word_reading', 'word': 'red', 'color': 'red', 'correct': 'f', 'soa': 2000},
         {'task': 'color_naming', 'word': 'green', 'color': 'green', 'correct': 'j',
          'soa': 1000}])


    def is_x(task, color, number):
        return task == 'w_r' and color == 'r' and number > 2


    def is_plus(task, color, number):
        return not is_x(task, color, number)


    x_shape = DerivedLevel('x', is_x, [
        TimelineVariable('task', ['w_r', 'c_n', 'n_n']),
        TimelineVariable('color', ['r', 'g', 'r']),
        TimelineVariable('number', [1, 2, 3]),
    ])

    y_shape = DerivedLevel('+', is_plus, [
        TimelineVariable('task', ['w_r', 'c_n', 'n_n']),
        TimelineVariable('color', ['r', 'g', 'r']),
        TimelineVariable('number', [1, 2, 3]),
    ])

    print(x_shape.to_psych())

    # print(train_sequence.sequence)
