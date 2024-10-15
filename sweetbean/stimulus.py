from abc import ABC, abstractmethod
from typing import List, TypeVar, Union

from sweetbean.parameter import (
    DataVariable,
    DerivedLevel,
    DerivedParameter,
    TimelineVariable,
    param_to_psych,
)

StringType = Union[None, str, DerivedParameter, TimelineVariable]
IntType = Union[None, int, TimelineVariable, DerivedParameter]
FloatType = Union[None, float, TimelineVariable, DerivedParameter]
StringTypeL = Union[List[StringType], StringType]
IntTypeL = Union[List[IntType], IntType]


class Stimulus(ABC):
    """
    A base class for stimuli
    """

    text_js = "{"
    text_trial = ""
    text_data = "on_finish: (data) => {"

    def __init__(self, args):
        if "self" in args:
            del args["self"]
        if "__class__" in args:
            del args["__class__"]
        self.arg = args
        self.arg_js = {}
        for key in args:
            self.arg_js[key] = param_to_psych(args[key])
        self.to_psych()

    def _type_to_psych(self):
        self.text_trial += f'type: {self.arg["type"]},'
        self.text_data += f'data["bean_type"] = \'{self.arg["type"]}\';'

    def _duration_to_psych(self):
        if "duration" in self.arg and self.arg["duration"] is not None:
            self.text_trial += self._set_param_js_preamble("trial_duration")
            self.text_trial += self._set_set_variable("duration")
            self.text_trial += "return "
            self.text_trial += self._set_get_variable("duration") + "},"
            self._set_data_text("duration")

    @abstractmethod
    def _stimulus_to_psych(self):
        pass

    def _choices_to_psych(self):
        if "choices" in self.arg and self.arg["choices"] is not None:
            self.text_trial += self._set_param_js_preamble("choices")
            self.text_trial += self._set_set_variable("choices")
            self.text_trial += "return "
            self.text_trial += self._set_get_variable("choices") + "},"
            self._set_data_text("choices")

    def _set_param_full(self, name):
        if name in self.arg and self.arg[name] is not None:
            self.text_trial += self._set_param_js_preamble(name)
            self.text_trial += self._set_set_variable(name)
            self.text_trial += "return "
            self.text_trial += self._set_get_variable(name) + "},"
            self._set_data_text(name)

    def _correct_to_psych(self):
        if "correct_key" in self.arg:
            self._set_data_text("correct_key")
            self.text_data += self._set_set_variable("correct")
            self.text_data += (
                'data["bean_correct"] = '
                + self._set_get_variable("correct_key")
                + '== data["response"]'
            )

    def to_psych(self):
        self._type_to_psych()
        self._duration_to_psych()
        self._stimulus_to_psych()
        self._choices_to_psych()
        self._correct_to_psych()
        self.text_js += self.text_trial + self.text_data + "}}"

    def to_image(self):
        pass

    def _set_param_js_preamble(self, param):
        return f"{param}: () => " + "{"

    def _set_data_text(self, param):
        self.text_data += self._set_set_variable(param)
        self.text_data += (
            f'data["bean_{param}"] = ' + self._set_get_variable(param) + ";"
        )

    def _set_set_variable(self, key):
        if key not in self.arg_js:
            return ""

        return f"let {key} = " + str(self.arg_js[key]) + ";"

    def _set_get_variable(self, key):
        if key not in self.arg_js:
            return ""
        if isinstance(self.arg_js[key], str) and self.arg_js[key].startswith("()"):
            return f"{key}()"
        return f"{key}"


StimulusVar = TypeVar("StimulusVar", bound=Stimulus)


class TextStimulus(Stimulus):
    """
    Show colored text
    """

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


class RandomObjectKinematogramStimulus(Stimulus):
    """
    Show a random-object-kinematogram
    """

    def __init__(
        self,
        duration: Union[None, int, TimelineVariable, DerivedParameter] = None,
        number_of_oobs: IntTypeL = 300,
        number_of_apertures: IntType = 1,
        coherent_movement_direction: IntTypeL = None,
        coherent_orientation: IntTypeL = None,
        coherence_movement: IntTypeL = 100,
        coherence_orientation: IntTypeL = 100,
        movement_speed: IntTypeL = 2,
        aperture_position_left: IntTypeL = 50,
        aperture_position_top: IntTypeL = 50,
        oob_color: StringTypeL = "white",
        background_color: StringType = "grey",
        stimulus_type: IntTypeL = 0,
        choices: List[str] = [],
        correct_key: StringType = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented // trial_duration
            number_of_oobs: the number of oriented objects per set in the stimulus
            number_of_apertures: the number of kinematograms
            coherent_movement_direction: the direction of coherent motion in degrees
                (0 degre meaning right)
            coherent_orientation: the orientation of the objects in degree
                (0 degree meaning right)
            coherence_movement: the percentage of oriented objects moving in the coherent direction.
            coherence_orientation: the percentage of oriented objects moving in the coherent
                direction.
            movement_speed: the movement speed of the oobs in (percentage of aperture_width)/second
            aperture_position_left: position of midpoint of aperture in x direction in percentage
                of window width
            aperture_position_top: position of midpoint of aperture in y direction in percentage
                of window height
            oob_color: the color of the orientated objects
            background_color: the background color
            choices: the valid keys that the subject can press to indicate a response
            correct_key: the correct key to press
        """
        type = "jsPsychRok"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self._set_param_full("number_of_oobs")
        self._set_param_full("number_of_apertures")
        self._set_param_full("coherent_movement_direction")
        self._set_param_full("coherent_orientation")
        self._set_param_full("coherence_movement")
        self._set_param_full("coherence_orientation")
        self._set_param_full("oob_color")
        self._set_param_full("background_color")
        self._set_param_full("movement_speed")
        self._set_param_full("aperture_position_left")
        self._set_param_full("aperture_position_top")
        self._set_param_full("correct_choice")
        self._set_param_full("stimulus_type")
        self.text_trial += self._set_param_js_preamble("correct_choice")
        self.text_trial += self._set_set_variable("correct_key")
        self.text_trial += "return [correct_key] },"

    def _correct_to_psych(self):
        if "correct_key" in self.arg:
            self._set_data_text("correct_key")
            self.text_data += self._set_set_variable("correct")
            self.text_data += 'data["bean_correct"] = data["correct"]'


ROKStimulus = RandomObjectKinematogramStimulus


class RandomDotPatternsStimulus(ROKStimulus):
    def __init__(
        self,
        duration: Union[None, int, TimelineVariable, DerivedParameter] = None,
        number_of_oobs: IntTypeL = 300,
        number_of_apertures: IntType = 2,
        coherent_orientation: IntTypeL = None,
        coherence_orientation: IntTypeL = 0,
        aperture_position_left: IntTypeL = 50,
        aperture_position_top: IntTypeL = 50,
        oob_color: StringTypeL = "white",
        background_color: StringType = "grey",
        stimulus_type: IntTypeL = 1,
        choices: List[str] = [],
        correct_key: StringType = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented // trial_duration
            number_of_oobs: the number of oriented objects per set in the stimulus
            number_of_apertures: the number of kinematograms
            coherent_movement_direction: the direction of coherent motion in degrees
                (0 degre meaning right)
            coherent_orientation: the orientation of the objects in degree
                (0 degree meaning right)
            coherence_movement: the percentage of oriented objects moving in the coherent direction.
            coherence_orientation: the percentage of oriented objects moving in the coherent
                direction.
            movement_speed: the movement speed of the oobs in (percentage of aperture_width)/second
            aperture_position_left: position of midpoint of aperture in x direction in percentage
                of window width
            aperture_position_top: position of midpoint of aperture in y direction in percentage
                of window height
            oob_color: the color of the orientated objects
            background_color: the background color
            choices: the valid keys that the subject can press to indicate a response
            correct_key: the correct key to press
        """

        super().__init__(
            duration=duration,
            number_of_oobs=number_of_oobs,
            number_of_apertures=number_of_apertures,
            coherent_movement_direction=0,
            coherent_orientation=coherent_orientation,
            coherence_movement=0,
            coherence_orientation=coherence_orientation,
            movement_speed=0,
            aperture_position_left=aperture_position_left,
            aperture_position_top=aperture_position_top,
            oob_color=oob_color,
            background_color=background_color,
            stimulus_type=stimulus_type,
            choices=choices,
            correct_key=correct_key,
        )


RDPStimulus = RandomDotPatternsStimulus


class ImageStimulus(Stimulus):
    """
    shows an image
    """

    def __init__(
        self,
        duration: IntType = None,
        src: str = "",
        choices: List[str] = [],
        correct_key: str = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the image
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychImageKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("src")
        self.text_trial += "return "
        self.text_trial += self._set_get_variable("src") + "},"
        self._set_data_text("src")


class VideoStimulus(Stimulus):
    """
    shows a video
    """

    def __init__(
        self,
        duration: IntType = None,
        src: List[str] = [""],
        choices: List[str] = [],
        correct_key: str = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            src: the path to the videos in different formats (needs to be a list)
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychVideoKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("src")
        self.text_trial += "return "
        self.text_trial += self._set_get_variable("src") + "},"
        self._set_data_text("src")


class BlankStimulus(TextStimulus):
    """
    shows a blank screen
    """

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


class SymbolStimulus(Stimulus):
    """
    show a symbol
    """

    def __init__(
        self,
        duration: IntType = None,
        symbol: str = "",
        color: str = "white",
        choices: List[str] = [],
        correct_key: str = "",
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            symbol: the symbol to show (allowed: square, triangle, circle)
            color: the color of the symbol
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
        """
        type = "jsPsychHtmlKeyboardResponse"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("stimulus")
        self.text_trial += self._set_set_variable("symbol")
        self.text_trial += self._set_set_variable("color")
        self.text_trial += "return "
        self.text_trial += (
            f'"<div class=\'sweetbean-"+{self._set_get_variable("symbol")}+"\' '
            f'style=\'background-color: "+{self._set_get_variable("color")}+"\'></div>"'
            "},"
        )
        self._set_data_text("symbol")
        self._set_data_text("color")


class SurveyStimulus(Stimulus):
    def __init__(self, args):
        super().__init__(args)

    def to_psych(self):
        self._type_to_psych()
        self._stimulus_to_psych()
        self.text_js += self.text_trial + self.text_data + "}}"


class TextSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyText"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': p})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")


class MultiChoiceSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyMultiChoice"
        super().__init__(locals())

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': Object.keys(p)[0],"
        self.text_trial += "options: p[Object.keys(p)[0]]})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")


class LikertSurveyStimulus(SurveyStimulus):
    def __init__(self, prompts=[]):
        type = "jsPsychSurveyLikert"
        super().__init__(locals())

    @classmethod
    def from_scale(cls, prompts=[], scale=[]):
        prompts_ = []
        for p in prompts:
            prompts_.append({p: scale})
        return cls(prompts_)

    def _stimulus_to_psych(self):
        self.text_trial += self._set_param_js_preamble("questions")
        self.text_trial += self._set_set_variable("prompts")
        self.text_trial += "\nlet prompts_ = []"
        self.text_trial += (
            f'\nfor (const p of {self._set_get_variable("prompts")})' + "{"
        )
        self.text_trial += "\nprompts_.push({'prompt': Object.keys(p)[0],"
        self.text_trial += "labels: p[Object.keys(p)[0]]})}"
        self.text_trial += "return prompts_},"
        self._set_data_text("prompts")
