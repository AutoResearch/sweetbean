from __future__ import annotations
from typing import List, Callable
import string
import random


class TimelineVariable:
    name: str = ''

    def __init__(self, name):
        self.name = str(name)

    def to_psych(self):
        return f"jsPsych.timelineVariable('{self.name}')"


def _param_to_psych(param):
    if isinstance(param, List):
        return param
    if isinstance(param, TimelineVariable) or isinstance(param, DerivedParameter):
        return param.to_psych()
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

    def __init__(self, text='', color='white', choices=[], correct='', duration=0):
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


class FlankerStimulus(Stimulus):
    type = 'jsPsychHtmlKeyboardResponse'
    def __init__(self, direction='left', distractor='left', color='white', choices=[], correct='', duration=0):
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


class Feedback(Stimulus):
    def __init__(self, duration: int = 0):
        self.duration = _param_to_psych(duration)
        if isinstance(duration, DerivedParameter):
            self.sequence_splicers.append(duration)

    def to_psych(self):
        res = '{'
        res += 'type: jsPsychHtmlKeyboardResponse,'
        res += f'trial_duration: {self.duration},'
        res += 'stimulus: () => {'
        res += 'let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;'
        res += 'if (last_trial_correct) {'
        res += 'return "<div class=' + "'feedback'" + '>Correct!</div>";'
        res += '} else {'
        res += 'let last_trial_response = jsPsych.data.get().last(1).values()[0].response;'
        res += 'if (last_trial_response) {'
        res += 'return "<div class=' + "'feedback'" + '>Wrong!</div>";'
        res += '} else {'
        res += 'return "<div class=' + "'feedback'" + '>Too slow!</div>";'
        res += '}'
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
