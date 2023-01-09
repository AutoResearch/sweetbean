from parameter import param_to_psych


class Stimulus:
    """
    A base class for visual stimuli
    """
    text_js = '{'
    text_trial = ''
    text_data = 'on_finish: (data) => {'

    def __init__(self, args):
        if 'self' in args:
            del args['self']
        if '__class__' in args:
            del args['__class__']
        self.arg = args
        self.arg_js = {}
        for key in args:
            self.arg_js[key] = param_to_psych(args[key])
        self.to_psych()

    def _type_to_psych(self):
        self.text_trial += f'type: {self.arg["type"]},'
        self.text_data += f'data["bean_type"] = {self.arg["type"]};'

    def _duration_to_psych(self):
        if 'duration' in self.arg and self.arg['duration'] is not None:
            self.text_trial += self._set_param_js_preamble('trial_duration')
            self.text_trial += self._set_set_variable('duration')
            self.text_trial += 'return '
            self.text_trial += self._set_get_variable('duration') + '},'
            self._set_data_text('duration')

    def _stimulus_to_psych(self):
        pass

    def _choices_to_psych(self):
        if 'choices' in self.arg and self.arg['choices'] is not None:
            self.text_trial += self._set_param_js_preamble('choices')
            self.text_trial += self._set_set_variable('choices')
            self.text_trial += 'return '
            self.text_trial += self._set_get_variable('choices') + '},'
            self._set_data_text('choices')

    def _correct_to_psych(self):
        if 'correct_key' in self.arg:
            self._set_data_text('correct_key')
            self.text_data += self._set_set_variable('correct')
            self.text_data += 'data["bean_correct"] = ' + self._set_get_variable('correct_key') + '== data["response"]'

    def to_psych(self):
        self._type_to_psych()
        self._duration_to_psych()
        self._stimulus_to_psych()
        self._choices_to_psych()
        self._correct_to_psych()
        self.text_js += self.text_trial + self.text_data + '}}'

    def to_image(self):
        pass

    def _set_param_js_preamble(self, param):
        return f'{param}: () => ' + '{'

    def _set_data_text(self, param):
        self.text_data += self._set_set_variable(param)
        self.text_data += f'data["bean_{param}"] = ' + self._set_get_variable(param) + ';'

    def _set_set_variable(self, key):
        if not key in self.arg_js:
            return ''
        return f'let {key} = {self.arg_js[key]};'

    def _set_get_variable(self, key):
        if not key in self.arg_js:
            return ''
        if isinstance(self.arg_js[key], str) and self.arg_js[key].startswith('()'):
            return f'{key}()'
        return f'{key}'


class TextStimulus(Stimulus):
    def __init__(self, duration=None, text='', color='white', choices=[], correct_key=''):
        type = 'jsPsychHtmlKeyboardResponse'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('stimulus')
        self.text_trial += self._set_set_variable('text')
        self.text_trial += self._set_set_variable('color')
        self.text_trial += 'return '
        self.text_trial += f'"<div style=\'color: "+{self._set_get_variable("color")}+"\'>"+{self._set_get_variable("text")}+"</div>"' + '},'
        self._set_data_text('text')
        self._set_data_text('color')