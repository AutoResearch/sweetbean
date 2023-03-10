from sweetbean.parameter import param_to_psych, DataVariable, DerivedLevel, DerivedParameter, TimelineVariable


class Stimulus:
    """
    A base class for stimuli
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
        self.text_data += f'data["bean_type"] = \'{self.arg["type"]}\';'

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
    """
    Show colored text
    """

    def __init__(self, duration: int = None, text: str = '', color: str = 'white', choices: list[str] = [],
                 correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            text: the text should be presented
            color: the color of the text
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
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


StroopStimulus = TextStimulus


class ImageStimulus(Stimulus):
    """
    shows an image
    """

    def __init__(self, duration: int = None, src: str = '', choices: list[str] = [], correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the image
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = 'jsPsychImageKeyboardResponse'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('stimulus')
        self.text_trial += self._set_set_variable('src')
        self.text_trial += 'return '
        self.text_trial += self._set_get_variable('src') + '},'
        self._set_data_text('src')


class VideoStimulus(Stimulus):
    """
    shows a video
    """

    def __init__(self, duration: int = None, src: list[str] = '', choices: list[str] = [], correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the videos in different formats (needs to be a list)
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = 'jsPsychVideoKeyboardResponse'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('stimulus')
        self.text_trial += self._set_set_variable('src')
        self.text_trial += 'return '
        self.text_trial += self._set_get_variable('src') + '},'
        self._set_data_text('src')


class BlankStimulus(TextStimulus):
    """
    shows a blank screen
    """

    def __init__(self, duration: int = None, choices: list[str] = [], correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        super().__init__(duration=duration, text='', choices=choices, correct_key=correct_key)


class FixationStimulus(TextStimulus):
    """
    show a white cross in the middle of the screen
    """

    def __init__(self, duration: int = None):
        """
        Arguments:
            duration: time in ms the stimulus is presented
        """
        super().__init__(duration=duration, text='+', color='white', choices=[], correct_key='')


class FeedbackStimulus(TextStimulus):
    """
    show the word correct or incorrect dependent on a correct response to a stimulus before
    """

    def __init__(self, duration: int = None, window: int = 1):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            window: how far back is the stimulus to check
                    (that stimulus needs to have a choice and a correct_key parameter)
        """
        correct = DataVariable('correct', [True, False])

        def is_correct(correct):
            return correct

        def is_false(correct):
            return not correct

        correct_feedback = DerivedLevel('correct', is_correct, [correct], window)
        false_feedback = DerivedLevel('false', is_false, [correct], window)

        feedback_text = DerivedParameter('feedback_text', [correct_feedback, false_feedback])
        super().__init__(duration, feedback_text)


class FlankerStimulus(TextStimulus):
    """
    show a flankert stimulus (<< < <<; << > <<, >> < >>, ...)
    """

    def __init__(self, duration: int = None, direction: str = 'left', distractor: str = 'left', choices: list[str] = [],
                 correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            direction: the direction of the target (allowed: left, right, l, r, L, R)
            distractor: the direction of the distractor (allowed: left, right, l, r, L, R)
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        target_text = '<'
        distractor_text = '<<'
        if not isinstance(direction, TimelineVariable) and (direction.lower() == 'right' or direction.lower() == 'r'):
            target_text = '>'
        if not isinstance(distractor, TimelineVariable) and (
                distractor.lower() == 'right' or distractor.lower() == 'r'):
            distractor_text = '>>'

        text = distractor_text + target_text + distractor_text

        if isinstance(direction, TimelineVariable) or isinstance(distractor, TimelineVariable):
            def is_left_left(t_dir, d_dir):
                return (t_dir.lower() == 'left' or t_dir.lower() == 'l') and (
                        d_dir.lower() == 'left' or d_dir.lower() == 'l')

            def is_left_right(t_dir, d_dir):
                return (t_dir.lower() == 'left' or t_dir.lower() == 'l') and (
                        d_dir.lower() == 'right' or d_dir.lower() == 'r')

            def is_right_left(t_dir, d_dir):
                return (t_dir.lower() == 'right' or t_dir.lower() == 'r') and (
                        d_dir.lower() == 'left' or d_dir.lower() == 'l')

            def is_right_right(t_dir, d_dir):
                return (t_dir.lower() == 'right' or t_dir.lower() == 'r') and (
                        d_dir.lower() == 'right' or d_dir.lower() == 'r')

            left_left = DerivedLevel('<<<<<', is_left_left, [direction, distractor])
            left_right = DerivedLevel('>><>>', is_left_right, [direction, distractor])
            right_left = DerivedLevel('<<><<', is_right_left, [direction, distractor])
            right_right = DerivedLevel('>>>>>', is_right_right, [direction, distractor])

            text = DerivedParameter('flanker_stimulus', [left_left, left_right, right_left, right_right])

        super().__init__(duration=duration, text=text, color='white', choices=choices, correct_key=correct_key)


class SymbolStimulus(Stimulus):
    """
    show a symbol
    """

    def __init__(self, duration: int = None, symbol: str = '', color: str = 'white', choices: list[str] = [],
                 correct_key: str = ''):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            symbol: the symbol to show (allowed: square, triangle, circle)
            color: the color of the symbol
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = 'jsPsychHtmlKeyboardResponse'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('stimulus')
        self.text_trial += self._set_set_variable('symbol')
        self.text_trial += self._set_set_variable('color')
        self.text_trial += 'return '
        self.text_trial += f'"<div class=\'sweetbean-"+{self._set_get_variable("symbol")}+"\' style=\'background-color: "+{self._set_get_variable("color")}+"\'></div>"' + '},'
        self._set_data_text('symbol')
        self._set_data_text('color')


class SurveyStimulus(Stimulus):
    def __init__(self, args):
        super().__init__(args)

    def to_psych(self):
        self._type_to_psych()
        self._stimulus_to_psych()
        self.text_js += self.text_trial + self.text_data + '}}'


class TextSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = 'jsPsychSurveyText'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('questions')
        self.text_trial += self._set_set_variable('prompts')
        self.text_trial += '\nlet prompts_ = []'
        self.text_trial += f'\nfor (const p of {self._set_get_variable("prompts")})' + '{'
        self.text_trial += '\nprompts_.push({\'prompt\': p})}'
        self.text_trial += 'return prompts_},'
        self._set_data_text('prompts')


class MultiChoiceSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = 'jsPsychSurveyMultiChoice'
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('questions')
        self.text_trial += self._set_set_variable('prompts')
        self.text_trial += '\nlet prompts_ = []'
        self.text_trial += f'\nfor (const p of {self._set_get_variable("prompts")})' + '{'
        self.text_trial += '\nprompts_.push({\'prompt\': Object.keys(p)[0],'
        self.text_trial += 'options: p[Object.keys(p)[0]]})}'
        self.text_trial += 'return prompts_},'
        self._set_data_text('prompts')


class LikertSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = 'jsPsychSurveyLikert'
        super().__init__(locals())

    @classmethod
    def from_scale(cls, prompts=[], scale=[]):
        prompts_ = []
        for p in prompts:
            prompts_.append({p: scale})
        return cls(prompts_)

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble('questions')
        self.text_trial += self._set_set_variable('prompts')
        self.text_trial += '\nlet prompts_ = []'
        self.text_trial += f'\nfor (const p of {self._set_get_variable("prompts")})' + '{'
        self.text_trial += '\nprompts_.push({\'prompt\': Object.keys(p)[0],'
        self.text_trial += 'labels: p[Object.keys(p)[0]]})}'
        self.text_trial += 'return prompts_},'
        self._set_data_text('prompts')
