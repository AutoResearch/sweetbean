import json

from sweetbean.stimulus.Stimulus import _KeyboardResponseStimulus


class Image(_KeyboardResponseStimulus):
    """
    shows an image
    """

    type = "jsPsychImageKeyboardResponse"

    def __init__(
        self,
        duration=None,
        stimulus="",
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        """
        Arguments:
            duration: time in ms the stimulus is presented
            stimulus: the path to the image
            choices: the keys that will be recorded if pressed
            correct_key: the correct key to press
            side_effects: a dictionary of side effects
        """
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _set_before(self):
        pass

    def _get_prompt_l(self):
        try:
            with open("image_prompts.json") as f:
                image_prompts = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "The file 'image_prompts.json' was not found. "
                "If you are using the Image stimulus, you need to provide a file "
                "'image_prompts.json' in the same directory as your experiment script. "
                "It should contain a dictionary with image paths as keys and prompts "
                "as values."
            )
        except json.JSONDecodeError:
            raise ValueError(
                "The file 'image_prompts.json' contains invalid JSON."
                "If you are using the Image stimulus, you need to provide a file "
                "'image_prompts.json' in the same directory as your experiment script. "
                "It should contain a dictionary with image paths as keys and prompts "
                "as values."
            )
        if not self.l_args["stimulus"] in image_prompts:
            raise ValueError(
                f"The image {self.l_args['stimulus']} is not in the image_prompts.json file."
                "If you are using the Image stimulus, you need to provide a file "
                "'image_prompts.json' in the same directory as your experiment script. "
                "It should contain a dictionary with image paths as keys and prompts "
                "as values."
            )

        return image_prompts[self.l_args["stimulus"]]
