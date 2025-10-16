from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus


class RSVP(_BaseStimulus):
    """
    RSVP stimulus (wraps the jsPsych RSVP plugin)
    """

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
        decorate_targets: bool = True,  # OFF by default
        target_shape: str = "none",  # default decoration
        target_stroke: str = "3px",
        targets: Optional[List[Dict[str, Any]]] = None,
        trial_duration: Optional[int] = None,
        record_timestamps: bool = True,
        duration: Optional[int] = None,
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            background (str | None):
                CSS color for the stimulus background. Default "#000000".
            color (str | None):
                CSS color for tokens when an item has no explicit color. Default "#ffffff".
            direction (str):
                Layout of the streams. "row" (left→right) or "column" (top→bottom).
                Default "row".
            stream_order (str | None):
                Comma-separated order of stream IDs as rendered (e.g., "left,right").
                If None and there are exactly two streams with direction=="row", the
                order is auto-filled to "<id0>,<id1>".
            gap (str):
                CSS gap between streams (e.g., "2rem", "24px"). Default "6rem".

            token_box_size (str):
                CSS size of each token’s containing box. Default "18vmin".
            token_font_size (str):
                CSS font size for tokens. Default "10vmin".
            token_padding (str):
                CSS padding inside each token box. Default "0.25em 0.45em".

            streams (list | None):
                List describing the RSVP streams. Each item is a dict:
                  {
                    "id": str,   # e.g., "left", "right"
                    "items": list[str] | TimelineVariable | FunctionVariable,
                    # optional:
                    "offset_ms": int,              # delay before first item in this stream
                    "attrs": dict[str, Any],       # extra per-stream attributes
                  }
                If a TimelineVariable/FunctionVariable is used for "items", it must
                evaluate per trial to list[str] (e.g., ["A","B","3","Q"]). Default [].

            stimulus_duration (int):
                Milliseconds each token is shown. Default 100.
            isi (int):
                Inter-stimulus interval within a stream (ms). Default 0.
            mask_html (str | None):
                Optional HTML mask shown between items. Default None.

            choices (str | list[str]):
                Allowed keys during RSVP:
                  • "ALL"      → any key is accepted
                  • "NO_KEYS"  → key presses ignored during RSVP
                  • list[str]  → explicit set, e.g., ["f","j"]
                Default "ALL".
            end_on_response (bool):
                If True and a valid key is pressed, the RSVP ends early. Default False.
            response_window (int | None):
                If set, time window (ms) during which responses are accepted. Default None.
            correct_keys (str | None):
                Comma-separated correct keys for scoring (e.g., "f,j"). Default None.

            decorate_targets (bool):
                Whether to visually decorate target items. Default True.
            target_shape (str):
                Default decoration shape used when a target omits "shape".
                Typical values: "circle", "square", "none". Default "none".
            target_stroke (str):
                CSS stroke width for target outlines (e.g., "3px", "4px"). Default "3px".
            targets (list | None):
                Target annotations (zero-based indices). Each item is a dict:
                  {
                    "stream_id": str,                                 # must match a stream "id"
                    "index": int | TimelineVariable | FunctionVariable,  # 0-based
                    # optional:
                    "shape": str | TimelineVariable | FunctionVariable,  # "circle"|"square"|"none"
                    "attrs": dict[str, Any],                           # extra per-target attributes
                  }
                Multiple targets may be specified. Default [].

            trial_duration (int | None):
                Overall RSVP duration (ms). If `duration` is provided (see below),
                it is mirrored into `trial_duration`. Default None.
            record_timestamps (bool):
                If True, records per-token presentation timestamps. Default True.
            duration (int | None):
                Generic SweetBean duration alias; when set, it is copied into
                `trial_duration` for convenience. Default None.
            side_effects (dict | None):
                Optional side-effect configuration passed to the runtime. Default None.

        Emits (added to jsPsych trial data):
            - bean_key (str | None): key pressed (if any).
            - bean_rt (number | None): reaction time (ms) for the key press.
            - bean_any_hit (bool): True if any declared target was hit.

        Notes:
            - Stream item lists and target indices are per-trial; use TimelineVariable
              or FunctionVariable to bind them from your timeline dicts.
            - Target indices are 0-based.
            - If exactly two streams are provided and direction=="row" and stream_order
              is not set, the order is auto-filled using the given stream IDs.
            - If `duration` is provided, it is mirrored into `trial_duration`.
        """
        if streams is None:
            streams = []
        if targets is None:
            targets = []
        if all(isinstance(s, str) for s in streams):
            identifier = ["left", "right"]
            if len(streams) > 2:
                identifier = [f"stream{i+1}" for i in range(len(streams))]
            streams = [
                {"id": identifier[idx], "items": list(str(s))}
                for idx, s in enumerate(streams)
            ]
        if all(isinstance(s, list) for s in streams):
            identifier = ["left", "right"]
            if len(streams) > 2:
                identifier = [f"stream{i+1}" for i in range(len(streams))]
            streams = [
                {"id": identifier[idx], "items": s} for idx, s in enumerate(streams)
            ]

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
