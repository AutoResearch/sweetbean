from sweetbean.stimulus.Stimulus import _KeyboardResponseStimulus
from sweetbean.variable import DataVariable, FunctionVariable


class HtmlKeyboardResponse(_KeyboardResponseStimulus):
    """
    A base class for html stimuli
    """

    type = "jsPsychHtmlKeyboardResponse"

    def __init__(
        self,
        duration=None,
        stimulus="",
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        if choices is None:
            choices = []
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _set_before(self):
        pass


class Text(HtmlKeyboardResponse):
    """
    Show colored text
    """

    l_template: str = (
        "You see "
        '{% if text %}"{{text}}" in "{{color}}"'
        "{% else %}a blank screen{% endif %}"
        "{% if duration %} for {{duration}}ms{% endif %}."
    )

    def __init__(
        self,
        duration=None,
        text="",
        color="white",
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            text: the text should be presented
            color: the color of the text
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            side_effects: a dictionary of side effects
        """
        if choices is None:
            choices = []

        def stim(cl, txt):
            return f"<div style='color:{cl}'>{txt}</div>"

        stimulus_ = FunctionVariable("stimulus", stim, [color, text])
        super().__init__(duration, stimulus_, choices, correct_key, side_effects)

        self.arg.update({"text": text, "color": color})


Stroop = Text


class Blank(HtmlKeyboardResponse):
    """
    shows a blank screen
    """

    def __init__(
        self,
        duration=None,
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            side_effects: a dictionary of side effects
        """
        super().__init__(
            duration=duration,
            stimulus="",
            choices=choices,
            correct_key=correct_key,
            side_effects=side_effects,
        )


class Fixation(Text):
    """
    show a white cross in the middle of the screen
    """

    def __init__(self, duration=None, side_effects=None):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            side_effects: a dictionary of side effects
        """
        super().__init__(
            duration=duration,
            text="+",
            color="white",
            choices=[],
            correct_key="",
            side_effects=side_effects,
        )


class Feedback(Text):
    """
    show the word correct or incorrect dependent on a correct response to a stimulus before
    """

    def __init__(
        self,
        duration=None,
        correct_message="Correct!",
        false_message="False!",
        correct_color="green",
        false_color="red",
        window=1,
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            correct_message: the message to show if the response was correct
            false_message: the message to show if the response was false
            correct_color: the color of the message if the response was correct
            false_color: the color of the message if the response was false
            window: how far back is the stimulus to check
                    (that stimulus needs to have a choice and a correct_key parameter)
            side_effects: a dictionary of side effects
        """
        correct = DataVariable("correct", window)

        feedback_txt = FunctionVariable(
            "feedback_txt",
            lambda c_msg, f_msg, cor: c_msg if cor else f_msg,
            [correct_message, false_message, correct],
        )

        feedback_color = FunctionVariable(
            "feedback_color",
            lambda c_color, f_color, cor: c_color if cor else f_color,
            [correct_color, false_color, correct],
        )

        super().__init__(
            duration,
            feedback_txt,
            feedback_color,
            choices=[],
            correct_key="",
            side_effects=side_effects,
        )


class Flanker(Text):
    """
    show a flanker stimulus (<< < <<; << > <<, >> < >>, ...)
    """

    def __init__(
        self,
        duration=None,
        direction="left",
        distractor="left",
        choices=None,
        correct_key="",
        color="white",
        n_flankers=2,
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            direction: the direction of the target (allowed: left, right, l, r, L, R)
            distractor: the direction of the distractor (allowed: left, right, l, r, L, R)
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            color: the color of the text
            n_flankers: the number of distractors
            side_effects: a dictionary of side effects
        """

        def _txt(dr, dst, n):
            normalized_dir = dr.lower()
            normalized_dist = dst.lower()
            t = ""
            d = ""
            if normalized_dir == "right" or normalized_dir == "r":
                t = ">"
            if normalized_dir == "left" or normalized_dir == "l":
                t = "<"
            if normalized_dist == "right" or normalized_dist == "r":
                d = ">"
            if normalized_dist == "left" or normalized_dist == "l":
                d = "<"
            d = d * n
            return f"{d}{t}{d}"

        txt = FunctionVariable("target", _txt, [direction, distractor, n_flankers])

        super().__init__(
            duration=duration,
            text=txt,
            color=color,
            choices=choices,
            correct_key=correct_key,
            side_effects=side_effects,
        )


class Symbol(HtmlKeyboardResponse):
    """
    show a symbol
    """

    def __init__(
        self,
        duration=None,
        symbol="",
        color="white",
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            symbol: the symbol to show (allowed: square, triangle, circle)
            color: the color of the symbol
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            side_effects: a dictionary of side effects
        """

        def stim(symbl, clr):
            return (
                f"<div class='sweetbean-{symbl}' style='background-color:{clr}'></div>"
            )

        stimulus_ = FunctionVariable("stimulus", stim, [symbol, color])
        super().__init__(duration, stimulus_, choices, correct_key, side_effects)
