from sweetbean.stimulus.Stimulus import _BaseStimulus


class TrolleyProblem(_BaseStimulus):
    """
    Show a trolley problem
    """

    type = "jsPsychTrolleyProblem"

    def __init__(self, main_track, side_track, side_effects=None):
        """
        Change this to match the arguments of the class
        """
        super().__init__(locals(), side_effects)

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        """
        This is used to process the arguments, generate a prompt and
        get a response from language input
        """
        main_track = self.l_args["main_track"]
        side_track = self.l_args["side_track"]

        people_dict = {
            "male_business": "businessman",
            "female_business": "businesswoman",
            "male_casual": "adult man",
            "female_casual": "adult woman",
            "male_elderly": "elderly man",
            "female_elderly": "elderly woman",
            "female_pregnant": "pregnant woman",
            "male_doctor": "male doctor",
            "female_doctor": "female doctor",
            "male_homeless": "homeless man",
            "female_homeless": "homeless woman",
            "male_bankRobber": "male bank robber",
            "female_bankRobber": "female bank robber",
        }

        def get_people_text_1(people):
            if not people or len(people) == 0:
                return "is nobody"
            if len(people) == 1:
                el = main_track[0]
                key = f"{el['gender']}_{el['body_type']}"
                return f"is a {el['skin']}, {people_dict[key]}"
            txt = "are "
            for i, el in enumerate(main_track):
                key = f"{el['gender']}_{el['body_type']}"
                if i == len(main_track) - 1:
                    txt += f"and a {el['skin']}, {people_dict[key]}"
                else:
                    txt += f"a {el['skin']}, {people_dict[key]}"
            return txt

        def get_people_text_2(people):
            if not people or len(people) == 0:
                return "nobody"
            if len(people) == 1:
                return "the person"

            return "the people"

        main_track_text_1 = get_people_text_1(main_track)
        side_track_text_1 = get_people_text_1(side_track)

        main_track_text_2 = get_people_text_2(main_track)
        side_track_text_2 = get_people_text_2(side_track)

        current_prompt = f"""
        You are standing by the railroad tracks when you notice an
        empty boxcar rolling out of control.
        It is moving so fast that anyone it hits will die.
        Ahead on the main track ${main_track_text_1}.
        There ${side_track_text_1} standing on a side track that doesn't rejoin the main track.
        If you do nothing, the boxcar will hit ${main_track_text_2} on the main track,
        but it will not hit ${side_track_text_2} the side track.
        If you pull a lever next to you,
        it will divert the boxcar to the side track where it will hit ${side_track_text_2},
        and not hit ${main_track_text_2} on the main track.
        Choose a track by answering a or b. a to do nothing, or b to pull the lever. You choose
        """
        if not multi_turn:
            in_prompt = " ".join([p for p in prompts]) + current_prompt + "<<"
        else:
            in_prompt = current_prompt + "<<"
        rest_data = None
        if not datum:
            _r = get_input(in_prompt)
            if isinstance(_r, str):
                response = _r
            elif isinstance(_r, dict):
                if "response" not in _r:
                    raise Exception(f"{_r} has an invalid response format")
                response = _r["response"]
                _r.pop("response")
                rest_data = _r
            else:
                raise Exception(f"{_r} has an invalid response format")

        else:
            response = datum["response"]

        prompts.append(current_prompt + f"<<{response}>>. ")

        data = self.l_args.copy()
        data.update(
            {
                "response": response,
            }
        )
        if rest_data:
            data.update(rest_data)
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
