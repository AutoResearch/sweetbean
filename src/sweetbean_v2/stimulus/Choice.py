import math

from sweetbean_v2.datatype.variables import FunctionVariable, to_js
from sweetbean_v2.stimulus.Stimulus import _BaseStimulus


class HtmlChoice(_BaseStimulus):
    """
    html elements that can be used to present a choice with a mouse press
    """

    type = "jsPsychHtmlChoice"

    def __init__(
        self,
        duration=None,
        html_array=None,
        values=None,
        time_after_response=0,
        side_effects=None,
    ):
        if values is None:
            values = []
        if html_array is None:
            html_array = []
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        pass

    def _process_response(self):
        self.js_data += 'data["bean_value"] = data["value"];'
        self.js_data += 'data["bean_choice"] = data["choice"];'

    def _set_before(self):
        pass


class Bandit(HtmlChoice):
    """
    A bandit task.
    """

    type = "jsPsychHtmlChoice"

    def __init__(
        self,
        duration=None,
        bandits=None,
        time_after_response=2000,
        side_effects=None,
    ):
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