from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus


class RSVP(_BaseStimulus):
    """
    RSVP stimulus (wraps the jsPsych RSVP plugin)
    """

    # IMPORTANT: the browser bundle must expose `window.jsPsychRsvp`.
    # Using a string type keeps SweetBean fully declarative.
    type = "jsPsychRsvp"

    def __init__(
        self,
        # Appearance / layout
        background: str = "#000000",
        color: str = "#ffffff",
        direction: str = "row",  # "row" | "column"
        stream_order: Optional[str] = None,  # e.g., "left,right"
        gap: str = "6rem",
        # Token sizing
        token_box_size: str = "18vmin",
        token_font_size: str = "10vmin",
        token_padding: str = "0.25em 0.45em",
        # Streams & timing (PLAIN DICTS)
        # streams: list of { id: str, items: list[str], offset_ms?: int, attrs?: {k:v} }
        streams: Optional[List[Dict[str, Any]]] = None,
        stimulus_duration: int = 100,
        isi: int = 0,
        mask_html: Optional[str] = None,
        # Responses
        choices: Union[str, List[str]] = "ALL",  # "ALL" | "NO_KEYS" | ["f","j"]
        end_on_response: bool = False,
        response_window: Optional[int] = None,  # None => unlimited
        correct_keys: Optional[str] = None,  # e.g., "f,j"
        # Targets (PLAIN DICTS)
        # targets: list of {
        #   stream_id: str, index: int, label?: str, response_window?: int|null,
        #   correct_keys?: ["f","j"]|"ALL"|null, shape?: "none"|"circle"|"square"|"underline",
        #   color?: str, stroke?: str, padding?: str
        # }
        decorate_targets: bool = True,  # OFF by default
        target_shape: str = "none",  # default decoration
        target_stroke: str = "3px",
        targets: Optional[List[Dict[str, Any]]] = None,
        # Lifetime / data
        trial_duration: Optional[int] = None,
        record_timestamps: bool = True,
        # SweetBean “duration” (optional) maps to trial_duration for parity with other stimuli
        duration: Optional[int] = None,
        # SweetBean side effects
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        if streams is None:
            streams = []
        if targets is None:
            targets = []

        super().__init__(locals(), side_effects)

    # ---- SweetBean hooks ----

    def _add_special_param(self):
        # Mirror other SweetBean stimuli: if `duration` is set, use it as `trial_duration`
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

        # Quality-of-life: if exactly two streams, left-to-right default order
        try:
            streams = self.arg_js.get("streams") or []
            if (
                (not self.arg_js.get("stream_order"))
                and self.arg_js.get("direction", "row") == "row"
                and len(streams) == 2
            ):
                a, b = streams[0].get("id"), streams[1].get("id")
                if a and b:
                    self.arg_js["stream_order"] = f"{a},{b}"
        except Exception:
            pass

    def _process_response(self):
        # Add SweetBean-style convenience fields to data
        self.js_data += 'data["bean_key"] = data["key_press"];'
        self.js_data += 'data["bean_rt"] = data["rt"];'
        self.js_data += (
            'data["bean_any_hit"] = '
            '(Array.isArray(data["targets"]) && data["targets"].some(t => t.hit));'
        )

    def _set_before(self):
        # No on_load JS needed; keep empty (consistent with your simple wrappers)
        pass

    # If you don’t support language mode, keep the default NotImplementedError like ROK:
    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError
