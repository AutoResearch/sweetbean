from typing import List


class TimelineVariable:
    name: str = ''

    def __init__(self, name):
        self.name = str(name)

    def to_psych(self):
        return f"jsPsych.timelineVariable('{self.name}')"


def _param_to_psych(param):
    if isinstance(param, TimelineVariable):
        return param.to_psych()
    else:
        return '"' + str(param) + '"'


class Stimulus:
    """
    A Template for other Stimuli
    """
    type: str = None
    duration: int = 0

    def to_psych(self):
        return 'hi'


class SimpleStimulus(Stimulus):
    type = 'jsPsychHtmlKeyboardResponse'
    v_shape: str = ''
    v_color: str = 'white'
    choices: List = []
    correct: str = ''

    def __init__(self, v_shape='', v_color='white', choices=[], correct='', duration=0):
        self.v_shape = _param_to_psych(v_shape)
        self.v_color = _param_to_psych(v_color)
        self.choices = _param_to_psych(choices)
        self.correct = _param_to_psych(correct)
        self.duration = _param_to_psych(duration)

    def to_psych(self):
        res = '{' \
               f'type: {self.type},' \
               f'trial_duration: {self.duration},' \
               'stimulus: () => { return '
        res += '"<div style='
        res += "'"
        res += 'color: " + '
        res += self.v_color
        res += ' + "\'>" +'
        res += self.v_shape
        res += " + '</div>'"
        res += '},'
        res += f'choices: {self.choices}'
        if self.correct:
            res += ','\
               'on_finish: (data) => {' \
               f'data["correct"] = {self.correct} == data["response"]'
            res += '}'

        res += '}'
        return res

class TrialSequence():
    def __init__ (self, sequence):
        self.sequence = sequence
    def to_psych(self):
        return f'{str(self.sequence)}'
