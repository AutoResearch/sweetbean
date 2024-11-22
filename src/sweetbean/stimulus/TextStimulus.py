from typing import List, Union

from sweetbean.parameter import (
    DataVariable,
    DerivedLevel,
    DerivedParameter,
    TimelineVariable,
)
from sweetbean.stimulus._Stimulus import Stimulus
from sweetbean.stimulus._utils import IntType, StringType


class TextStimulus(Stimulus):
    """
    Show colored text
    """

    base_template = (
        "{% if text %}"
        'You see "{{ text }}" written in {{ color }}'
        "{% else %}"
        "You see a blank screen"
        "{% endif %}"
    )

    def __init__(
        self,
        duration: Union[None, int, TimelineVariable, DerivedParameter] = None,
        text: StringType = "",
        color: StringType = "white",
        choices: List[str] = [],
        correct_key: StringType = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            text: the text should be presented
            color: the color of the text
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychHtmlKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("text")
        self.text_trial += self._set_set_variable("color")
        self.text_trial += "return "
        self.text_trial += (
            f'"<div style=\'color: "+{self._set_get_variable("color")}+"\'>"'
            f'+{self._set_get_variable("text")}+"</div>"'
            "},"
        )
        self._set_data_text("text")
        self._set_data_text("color")


StroopStimulus = TextStimulus


class BlankStimulus(TextStimulus):
    """
    shows a blank screen
    """

    base_template = "You see a blank screen"

    def __init__(
        self,
        duration: IntType = None,
        choices: List[str] = [],
        correct_key: StringType = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        super().__init__(
            duration=duration, text="", choices=choices, correct_key=correct_key
        )


class FixationStimulus(TextStimulus):
    """
    show a white cross in the middle of the screen
    """

    base_template = "You see a white cross in the middle of the screen"

    def __init__(self, duration: IntType = None):
        """
        Arguments:
            duration: time in ms the stimulus is presented
        """
        super().__init__(
            duration=duration, text="+", color="white", choices=[], correct_key=""
        )


class FeedbackStimulus(TextStimulus):
    """
    show the word correct or incorrect dependent on a correct response to a stimulus before
    """

    template = (
        '{% if feedback_text %} You see "{{ feedback_text }}"'
        "{% else %} You see a blank screen {% endif %}"
    )

    def __init__(
        self,
        duration: IntType = None,
        window: int = 1,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            window: how far back is the stimulus to check
                    (that stimulus needs to have a choice and a correct_key parameter)
        """
        correct = DataVariable("correct", [True, False])

        def is_correct(correct):
            return correct

        def is_false(correct):
            return not correct

        correct_feedback = DerivedLevel("correct", is_correct, [correct], window)
        false_feedback = DerivedLevel("false", is_false, [correct], window)

        feedback_text = DerivedParameter(
            "feedback_text", [correct_feedback, false_feedback]
        )
        super().__init__(duration, feedback_text)


class FlankerStimulus(TextStimulus):
    """
    show a flankert stimulus (<< < <<; << > <<, >> < >>, ...)
    """

    base_template = (
        'You see "'
        "{% if distractor == left %}"
        "<<"
        "{% else %}"
        ">>"
        "{% endif %}"
        "{% if direction == left %}"
        "<"
        "{% else %}"
        ">"
        "{% endif %}"
        "{% if distractor == left %}"
        "<<"
        "{% else %}"
        ">>"
        "{% endif %}"
        '"'
    )

    def __init__(
        self,
        duration: IntType = None,
        direction: StringType = "left",
        distractor: StringType = "left",
        choices: List[str] = [],
        correct_key: StringType = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            direction: the direction of the target (allowed: left, right, l, r, L, R)
            distractor: the direction of the distractor (allowed: left, right, l, r, L, R)
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        target_text = "<"
        distractor_text = "<<"
        if (
            direction
            and not isinstance(direction, (TimelineVariable, DerivedParameter))
            and (direction.lower() == "right" or direction.lower() == "r")
        ):
            target_text = ">"
        if (
            distractor
            and not isinstance(distractor, (TimelineVariable, DerivedParameter))
            and (distractor.lower() == "right" or distractor.lower() == "r")
        ):
            distractor_text = ">>"

        if not isinstance(direction, TimelineVariable) and not isinstance(
            distractor, TimelineVariable
        ):
            text = distractor_text + target_text + distractor_text
            super().__init__(
                duration=duration,
                text=text,
                color="white",
                choices=choices,
                correct_key=correct_key,
            )
        else:

            def is_left_left(t_dir, d_dir):
                return (t_dir.lower() == "left" or t_dir.lower() == "l") and (
                    d_dir.lower() == "left" or d_dir.lower() == "l"
                )

            def is_left_right(t_dir, d_dir):
                return (t_dir.lower() == "left" or t_dir.lower() == "l") and (
                    d_dir.lower() == "right" or d_dir.lower() == "r"
                )

            def is_right_left(t_dir, d_dir):
                return (t_dir.lower() == "right" or t_dir.lower() == "r") and (
                    d_dir.lower() == "left" or d_dir.lower() == "l"
                )

            def is_right_right(t_dir, d_dir):
                return (t_dir.lower() == "right" or t_dir.lower() == "r") and (
                    d_dir.lower() == "right" or d_dir.lower() == "r"
                )

            left_left = DerivedLevel("<<<<<", is_left_left, [direction, distractor])
            left_right = DerivedLevel(">><>>", is_left_right, [direction, distractor])
            right_left = DerivedLevel("<<><<", is_right_left, [direction, distractor])
            right_right = DerivedLevel(">>>>>", is_right_right, [direction, distractor])

            text_d = DerivedParameter(
                "flanker_stimulus", [left_left, left_right, right_left, right_right]
            )
            super().__init__(
                duration=duration,
                text=text_d,
                color="white",
                choices=choices,
                correct_key=correct_key,
            )
