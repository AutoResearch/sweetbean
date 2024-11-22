from typing import List, Union

from sweetbean.parameter import DerivedParameter, TimelineVariable
from sweetbean.stimulus._Stimulus import Stimulus
from sweetbean.stimulus._utils import (
    IntType,
    IntTypeL,
    StringType,
    StringTypeL,
    add_warning,
)


class RandomObjectKinematogramStimulus(Stimulus):
    """
    Show a random-object-kinematogram
    """

    base_template = (
        "You see {{ number_of_oobs }} moving "
        "{{ if stimulus_type == 0}} triangles"
        "{{ elif stimulus_type == 1}} circles"
        "{{ elif stimulus_type == 2}} squares"
        "{{ elif stimulus_type == 3}} stylist birds"
        ". "
        "{{ endif }} "
        "They are {{ oob_color }}. "
        "The background is {{ background_color }}. "
        "{{ coherence_movement }} of the objects are moving in the same direction. "
        "The rest moves randomly. "
        "The speed is {{ movement_speed }}. "
        "This direction is {{ coherent_movement_direction }} degree. "
        "{{ coherence_orientation }} of the objects are oriented in the same direction. "
        "The rest is orientated randomly. "
        "This orientation is {{ coherent_orientation }} degree"
    )
    duration_template = (
        "{% if duration %} You see them move for {{ duration }} ms{% endif %}"
    )

    @add_warning(lambda x: x != 1)
    def number_of_apertures(self):
        return self.number_of_apertures

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
            coherent_orientation: the orientation of the objects in degree
                (0 degree meaning right)
            coherence_orientation: the percentage of oriented objects moving in the coherent
                direction.
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
