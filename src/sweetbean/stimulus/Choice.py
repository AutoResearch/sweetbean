import math

from sweetbean.stimulus.Stimulus import _BaseStimulus
from sweetbean.util.parse import to_js
from sweetbean.variable import FunctionVariable


class HtmlChoice(_BaseStimulus):
    """
    Clickable HTML choice screen.

    Renders an array of arbitrary HTML elements; a mouse click selects one item.
    Records `choice` (0-based index) and `value` of the selected item from the
    provided lists, and mirrors them to `bean_response` and `bean_value`.
    Supports an optional post-response delay to allow animations to complete.
    """

    type = "jsPsychHtmlChoice"

    def __init__(
        self,
        duration=None,
        html_array=None,
        values=None,
        time_after_response=3000,
        side_effects=None,
    ):
        """
        Arguments:
            duration (int | None): Stimulus display time in ms. If None, runs until a choice is
                made.
            html_array (list): List of HTML strings to display as clickable options. Must align 1:1
                with `values`.
            values (list): List of opaque values (numbers/strings/objects) mapped to `html_array`
                items. The selected entry is emitted as both `value` and `bean_value`.
            time_after_response (int): Extra time in ms after a click before ending the trial
                (useful for short animations/visual confirmation).
            side_effects (dict | None): Optional side-effect configuration passed through to the
            runtime.

        Emits (adds to jsPsych data):
            - choice (int): 0-based index of the clicked item
            - value (any): the corresponding entry from `values`
            - bean_response (int): copy of `choice` for downstream consistency
            - bean_value (any): copy of `value`

        Notes:
            - `len(html_array)` should equal `len(values)`. Empty lists are allowed but will yield
                no clickable options.
            - This stimulus collects responses via mouse/touch clicks on the provided elements.
        """
        if values is None:
            values = []
        if html_array is None:
            html_array = []
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_value"] = data["value"];'
        self.js_data += 'data["bean_response"] = data["choice"];'

    def _set_before(self):
        pass

    def process_l(self, prompts, get_input, multi_turn):
        raise NotImplementedError


class Bandit(HtmlChoice):
    """
    Multi-armed bandit screen built on HtmlChoice.

    Displays N colored “slot machine” squares laid out in a grid. Clicking a square
    selects that bandit. The grid HTML and the `values` array are generated from
    `bandits=[{"color": <css_color>, "value": <number/label>}, ...]`. Records the
    selected index as `choice` and its associated `value`, mirrored to `bean_response`
    and `bean_value`. Exposes a short post-response window that shows the value of the
    chosen bandit.
    """

    type = "jsPsychHtmlChoice"

    def __init__(
        self,
        duration=None,
        bandits=None,
        time_after_response=2000,
        side_effects=None,
    ):
        """
        Arguments:
            duration (int | None): Stimulus display time in ms. If None, runs until a bandit is
                chosen.
            bandits (list): List of dicts, each with:
                - color (str): CSS color to outline the square
                - value (any): payout/label recorded when the bandit is chosen
            time_after_response (int): Extra time in ms after a click for “slot machine” animation.
            side_effects (dict | None): Optional side-effect configuration.

        Layout & styling:
            - Squares are arranged in a near-square grid (rows × cols) computed from N.
            - CSS custom properties are set before the trial:
                --slotmachine-time, --slotmachine-time-after  (both ~ time_after_response/2)

        Emits (adds to jsPsych data) — same as HtmlChoice:
            - choice (int), value (any), bean_response (int), bean_value (any)
        """
        if bandits is None:
            bandits = []

        def bandits_to_html(bdts):
            n = len(bdts)
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)

            # Calculate square size
            square_width = (100 - (cols + 1) * 10) / cols
            square_height = (100 - (rows + 1) * 10) / rows
            square_size = min(square_width, square_height)

            # Generate square positions
            positions = []
            for r in range(rows):
                # Calculate the number of squares in this row
                if r == rows - 1 and n % cols != 0:  # Last row and it's not full
                    row_squares = n % cols
                else:
                    row_squares = cols

                # Calculate the starting x position to center the row
                total_row_width = row_squares * square_size + (row_squares - 1) * 10
                start_x = (100 - total_row_width) / 2

                for c in range(row_squares):
                    x = start_x + c * (square_size + 10)
                    y = 10 + r * (square_size + 10)
                    positions.append((x, y, square_size))
            html = []
            for bdt, p in zip(bdts, positions):
                html.append(
                    f'<div class="slotmachine" '
                    f'style="position: absolute; top:{p[1]}vh; left:{p[0]}vw; '
                    f'width: {p[2]}vw; height: {p[2]}vh; border-color: {bdt["color"]}">'
                    f"</div>"
                )
            return html

        def vals(bdts):
            return [b["value"] for b in bdts]

        html_array = FunctionVariable("html_array", bandits_to_html, [bandits])
        values = FunctionVariable("values", vals, [bandits])

        super().__init__(
            duration=duration,
            html_array=html_array,
            values=values,
            time_after_response=time_after_response,
            side_effects=side_effects,
        )
        self.arg.update({"bandits": bandits})

    def _set_before(self):
        res = "const root=document.documentElement;"
        res += (
            f'root.style.setProperty("--slotmachine-time",'
            f'`${{({to_js(self.arg_js["time_after_response"])})/2}}ms`);'
        )
        res += (
            f'root.style.setProperty("--slotmachine-time-after",'
            f'`${{({to_js(self.arg_js["time_after_response"])})/2}}ms`);'
        )
        self.js_before = f"on_load:()=>{{{res}}},"

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        current_prompt = f' You see {len(self.l_args["bandits"])} bandits.'
        for idx, bandit in enumerate(self.l_args["bandits"]):
            current_prompt += f' Bandit {idx + 1} is {bandit["color"]}.'
        current_prompt += (
            " Choose a bandit by naming the number of the bandit. You name "
        )
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
            # response = get_input(in_prompt)
        else:
            response = datum["response"] + 1
        if int(response) < 1 or int(response) > len(self.l_args["bandits"]):
            prompts.append(
                current_prompt + f"<<{response}>>. " f"The response was invalid."
            )
            value = 0
        else:
            prompts.append(
                current_prompt + f"<<{response}>>. "
                f"The value of the chosen bandit was {self.l_args['values'][int(response) - 1]}."
            )
            value = self.l_args["values"][int(response) - 1]
        data = self.l_args.copy()
        data.update(
            {
                "response": int(response) - 1,
                "value": value,
            }
        )
        if rest_data:
            data.update(rest_data)
        return data, prompts
