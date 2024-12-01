from sweetbean.stimulus.Stimulus import _BaseStimulus


class _Template_(_BaseStimulus):
    """
    A template for creating a new stimulus.
    The following methods are probably sufficient to implement.
    """

    def __init__(self, args, side_effects=None):
        """
        Change this to match the arguments of the class
        """
        super().__init__(args, side_effects)

    def process_l(self, prompts, get_input, multi_turn, datum):
        """
        This is used to process the arguments, generate a prompt and
        get a response from language input
        """
        data = self.l_args.copy()
        # Add your code for prompt generation here:

        # Add your code for processing the response and adding to data here:
        return data, prompts

    def _add_special_param(self):
        """
        This can be used to add special parameters to the js object that are
        not input arguments of the class
        """
        pass

    def _process_response(self):
        """
        This can be used to process the responses given by the participant and
        adding data to the js object
        """
        pass

    def _set_before(self):
        """
        This can be used to set global parameters before the stimulus is presented
         (for example css variables)
        """
        pass
