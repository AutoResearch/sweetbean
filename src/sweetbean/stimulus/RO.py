from sweetbean.stimulus.Stimulus import _BaseStimulus


class RandomObjectKinematogram(_BaseStimulus):
    """
    Show a random-object-kinematogram
    """

    type = "jsPsychRok"

    def __init__(
        self,
        duration=None,
        number_of_oobs=300,
        number_of_apertures=1,
        coherent_movement_direction=180,
        coherent_orientation=180,
        coherence_movement=100,
        coherence_orientation=100,
        movement_speed=10,
        aperture_position_left=50,
        aperture_position_top=50,
        oob_color="white",
        background_color="black",
        stimulus_type=0,
        choices=None,
        correct_key="",
        side_effects=None,
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
            side_effects: a dictionary of side effects
        """
        if choices is None:
            choices = []
        correct_choice = [correct_key]
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_correct"]=data["correct"];'

    def _set_before(self):
        pass

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError


ROK = RandomObjectKinematogram


class RandomDotPatterns(ROK):
    def __init__(
        self,
        duration=None,
        number_of_oobs=300,
        number_of_apertures=2,
        coherent_orientation=0,
        coherence_orientation=0,
        aperture_position_left=50,
        aperture_position_top=50,
        oob_color="white",
        background_color="grey",
        stimulus_type=1,
        choices=None,
        correct_key="",
        side_effects=None,
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
            side_effects: a dictionary of side effects
        """
        if choices is None:
            choices = []

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
            side_effects=side_effects,
        )


RDP = RandomDotPatterns
