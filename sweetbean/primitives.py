from __future__ import annotations
from typing import List, Callable


class TimelineVariable:
    name: str = ''

    def __init__(self, name):
        self.name = str(name)

    def to_psych(self):
        return f"jsPsych.timelineVariable('{self.name}')"


def _param_to_psych(param):
    if param is None:
        return 'null'
    elif isinstance(param, List):
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

    def splice_into_sequence(self, trial_sequence):
        for s in self.sequence_splicers:
            s.splice_into_sequence(trial_sequence)


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
        res = '{' \
              f'type: {self.type},' \
              f'trial_duration: {self.duration},' \
              'stimulus: () => { return '
        res += '"<div style='
        res += "'"
        res += 'color: " + '
        res += self.color
        res += ' + "\'>" +'
        res += self.text
        res += " + '</div>'"
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct:
            res += ',' \
                   'on_finish: (data) => {' \
                   f'data["correct"] = {self.correct} == data["response"]'
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
        res = '{' \
              f'type: {self.type},' \
              f'trial_duration: {self.duration},' \
              'stimulus: () => { '
        res += 'let c = "sweetbean-"+jsPsych.timelineVariable(\'symbol\');'
        res += 'return '
        res += f'"<div class=\'" + c + "\' style=" + '
        res += '"\'background: " + ('
        res += self.symbol + ' == "triangle" ? "transparent" : ' + self.color + ')'
        res += ' + (' + self.symbol + ' == "triangle" ? "; border-bottom: solid 10vw " + ' + self.color + ' : "") '
        res += ' + "\'></div>"'
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct:
            res += ',' \
                   'on_finish: (data) => {' \
                   f'data["correct"] = {self.correct} == data["response"]'
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
        if self.correct:
            res += ',' \
                   'on_finish: (data) => {' \
                   f'data["correct"] = {self.correct} == data["response"]'
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
        res += 'response_ends_trial: () => {'
        res += 'if (' + self.correct + '){ return true;'
        res += '} else {'
        res += 'return true;}},'
        res += f'choices: {self.choices}'
        if self.correct:
            res += ',' \
                   'on_finish: (data) => {' \
                   f'data["correct"] = {self.correct} == data["response"]'
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

    def splice(self, param_name, trial_sequence):
        name_lis = [f.name for f in self.factors]
        for trial in trial_sequence.sequence:
            args = [trial[name] for name in name_lis]
            if self.predicate(*args):
                trial[param_name] = self.value


class DerivedParameter:
    name: str
    levels: List[DerivedLevel]

    def __init__(self, name, levels):
        self.name = name
        self.levels = levels

    def to_psych(self):
        return f"jsPsych.timelineVariable('{self.name}')"

    def splice_into_sequence(self, sequence):
        for l in self.levels:
            l.splice(self.name, sequence)


if __name__ == '__main__':
    train_sequence = TrialSequence(
        [{'task': 'word_reading', 'word': 'red', 'color': 'red', 'correct': 'f', 'soa': 2000},
         {'task': 'color_naming', 'word': 'green', 'color': 'green', 'correct': 'j',
          'soa': 1000}])


    def is_x(task):
        return task == 'word_reading'


    x_shape = DerivedLevel('x', is_x, [TimelineVariable('task')])

    x_shape._splice('fixation_shape', train_sequence)

    print(train_sequence.sequence)
