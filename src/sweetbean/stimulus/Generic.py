import warnings

from sweetbean.stimulus.Stimulus import _BaseStimulus


class Generic(_BaseStimulus):
    """
    A generic stimulus.

    Attention: This stimulus implements jsPsych stimuli but can not be
        used to run experiments on language
    """

    _not_tested: bool = False
    _js_plugins: list = []

    def __init__(
        self,
        side_effects=None,
        **kwargs,
    ):
        if "type" not in kwargs:
            raise ValueError("`type` argument must be defined in Generic stimulus.")
        if not Generic._not_tested:
            warnings.warn(
                "You are using a Generic Stimulus. This feature has not been fully tested.\n"
                "It might work for creating html files or javascript functions but probably\n"
                "will not work with running experiments on language."
            )
            Generic._not_tested = True
        if not kwargs["type"] in Generic._js_plugins:
            warnings.warn(
                f"You are using a jsPsych plugin {kwargs['type']} with a generic class.\n"
                f"Make sure to add the script plugin to the generated HTML file\n"
                f"or javascript function. You can find a list here:\n"
                f"https://www.jspsych.org/v7/plugins/list-of-plugins/\n"
            )
            Generic._js_plugins.append(kwargs["type"])

        self.side_effects = side_effects
        if "self" in kwargs:
            del kwargs["self"]
        if "__class__" in kwargs:
            del kwargs["__class__"]
        if "side_effects" in kwargs:
            del kwargs["side_effects"]

        self.arg = kwargs
        self.arg_js = {}
        if "duration" in self.arg:
            self.arg_js["trial_duration"] = self.arg["duration"]
        for key in self.arg:
            self.arg_js[key] = kwargs[key]

    def _add_special_param(self):
        pass

    def _process_response(self):
        pass

    def _set_before(self):
        pass
