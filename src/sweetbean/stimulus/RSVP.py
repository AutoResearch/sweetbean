from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus


class RSVP(_BaseStimulus):
    """
    General RSVP wrapper for your jsPsych plugin: window.jsPsychRsvp
    (plugin name: "rsvp" / class var: jsPsychRsvp)

    ✅ Supports:
      - streams (object form preferred)
      - targets: [{stream_id, index, ...}]
      - distractors: [{stream_id, index, ...}]
      - decorate_targets / decorate_distractors and default shapes/colors
      - response options, timing, sizing, etc.

    ⚠️ Short-form streams are only normalized when it's obviously safe:
       • [["A","B"],["Q","O"]] → [{"id":"left","items":[...]}, {"id":"right",...}]
       • ["ABQQ","OOXO"] → split to characters per stream
       If any element is a Variable (FunctionVariable/TimelineVariable/DataVariable),
       we pass through untouched — do your char-splitting inside the mapping fn.

    Extra quality-of-life:
      - If exactly two streams in "row" and no stream_order, we auto "id0,id1".
      - If any distractor omits `index` and there is exactly one target, we copy
        that target's `index` (works with ints or variable placeholders).
      - `end_on_response` (SweetBean convenience) is mapped to plugin’s
        `response_ends_trial`.
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
        # Streams & timing
        streams: Optional[List[Any]] = None,  # preferred: [{"id":..., "items": [...]}]
        stimulus_duration: int = 100,
        isi: int = 0,
        mask_html: Optional[str] = None,
        # Responses
        choices: Union[str, List[str]] = "ALL",  # "ALL" | "NO_KEYS" | ["f","j"]
        end_on_response: bool = False,  # convenience -> response_ends_trial
        response_window: Optional[int] = None,  # None → unlimited
        correct_keys: Optional[str] = None,  # e.g., "f,j"
        # Targets (timing + decoration)
        decorate_targets: bool = True,
        target_shape: str = "none",
        target_stroke: str = "3px",
        targets: Optional[List[Dict[str, Any]]] = None,
        # Distractors (decoration only)
        decorate_distractors: bool = False,
        distractor_shape: str = "none",
        distractor_color: str = "#888888",
        distractor_stroke: str = "2px",
        distractors: Optional[List[Dict[str, Any]]] = None,
        # Lifetime
        trial_duration: Optional[int] = None,
        # Data options
        record_timestamps: bool = True,
        # SweetBean generic
        duration: Optional[int] = None,
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            background:
                CSS color for the stimulus background. Default "#000000".
            color:
                CSS color used for token text (and the default border color when not
                otherwise specified). Default "#ffffff".
            direction:
                Stream layout: "row" (left–right) or "column" (top–bottom). Default "row".
            stream_order:
                Comma-separated order of stream IDs in the DOM (e.g., "left,right").
                If omitted and there are exactly two streams in "row" layout, the order
                is auto-filled from the two stream IDs.
            gap:
                CSS gap between streams in non-bilateral layouts. Default "6rem".

            token_box_size:
                CSS size for each fixed token box (prevents wobble when borders appear).
                Default "18vmin".
            token_font_size:
                CSS font size for the characters inside each token box. Default "10vmin".
            token_padding:
                CSS padding used inside the decoration outline. Default "0.25em 0.45em".

            streams:
                Per-trial stream specifications. Prefer object form:
                  [
                    {"id": "left",  "items": ["O","Q","O",...]},
                    {"id": "right", "items": ["1","2","3",...]}
                  ]
                Short forms are normalized only when obviously safe *and literal*:
                  • ["ABQQ","OOXO"] → [{"id":"left","items":["A","B","Q","Q"]}, ...]
                  • [["A","B"],["Q","O"]] → [{"id":"left","items":["A","B"]}, ...]
                If any element is a Variable (FunctionVariable / TimelineVariable /
                DataVariable), the list is passed through untouched—perform any splitting
                inside your mapping functions.

            stimulus_duration:
                Milliseconds each token is displayed. Default 100.
            isi:
                Inter-stimulus interval (ms) between tokens in a stream. Default 0.
            mask_html:
                Optional HTML string shown between tokens (e.g., "•"). Default None.

            choices:
                Which keys are allowed during the RSVP:
                  - "ALL": any key is accepted
                  - "NO_KEYS": keypresses are ignored during RSVP
                  - list[str]: explicit set (e.g., ["f","j"])
                Default "ALL".
            end_on_response:
                If True, the RSVP ends immediately after the first valid keypress.
                This maps to the plugin’s `response_ends_trial`. Default False.
            response_window:
                Optional global time window in ms for responses. Per-target windows may
                override this. Default None → unlimited.
            correct_keys:
                Optional comma-separated string for scoring (e.g., "f,j"). Default None.

            decorate_targets:
                Whether to visually decorate targets. Decoration is only visible if
                the shape is not "none". Default True.
            target_shape:
                Default target decoration shape: "circle" | "square" | "underline" | "none".
                This is used when a target omits `shape`. Default "none".
            target_stroke:
                CSS stroke width for target outlines (e.g., "3px", "4px"). Default "3px".
            targets:
                List of target annotations (zero-based indices). Each item:
                  {
                    "stream_id": str,
                    "index": int | Variable,
                    # optional:
                    "label": str,
                    "response_window": int | None,
                    "correct_keys": list[str] | "ALL" | None,
                    "shape": "circle"|"square"|"underline"|"none",
                    "color": str,
                    "stroke": str,
                    "padding": str,
                  }

            decorate_distractors:
                Whether to decorate explicit distractor positions. Default False.
            distractor_shape:
                Default distractor decoration shape if an item omits `shape`.
                Default "none".
            distractor_color:
                Default stroke/text color for distractors when not overridden.
                Default "#888888".
            distractor_stroke:
                Default border width for distractors (e.g., "2px"). Default "2px".
            distractors:
                List of explicit distractor annotations (decoration only). Each item:
                  {
                    "stream_id": str,
                    "index": int | Variable,     # if omitted and exactly one target exists,
                                                 # the index is copied from that target
                    # optional:
                    "label": str,
                    "shape": "circle"|"square"|"underline"|"none",
                    "color": str,
                    "stroke": str,
                    "padding": str,
                  }

            trial_duration:
                Hard stop for the RSVP (ms). If not set, the trial ends after the last
                token (plus ISI). Default None.
            record_timestamps:
                If True, record per-token onset/offset times into `data.schedule`.
                Default True.
            duration:
                SweetBean convenience alias; when set, it is mirrored into
                `trial_duration`.
            side_effects:
                Optional dictionary of side effects to pass along at runtime.

        Emits (added to jsPsych trial data):
            - bean_key (str | None): first key pressed (if any).
            - bean_rt (number | None): RT (ms) of the first keypress.
            - bean_any_hit (bool): whether any declared target was hit.
        """
        if streams is None:
            streams = []
        if targets is None:
            targets = []
        if distractors is None:
            distractors = []

        # ---- Only normalize short forms when it's obviously safe (pure literals) ----
        def _all_str_list(x: Any) -> bool:
            return isinstance(x, list) and all(isinstance(t, str) for t in x)

        try:
            if isinstance(streams, list) and len(streams) > 0:
                # Case 1: ["ABCD","QOQQ"] → characters per stream
                if all(isinstance(s, str) for s in streams):
                    ids = (
                        ["center"]
                        if len(streams) == 1
                        else (
                            ["left", "right"]
                            if len(streams) == 2
                            else [f"s{i+1}" for i in range(len(streams))]
                        )
                    )
                    streams = [
                        {"id": ids[i], "items": list(s)} for i, s in enumerate(streams)
                    ]

                # Case 2: [["A","B"],["Q","O"]] → object form if all inner items are strings
                elif all(_all_str_list(s) for s in streams):
                    ids = (
                        ["center"]
                        if len(streams) == 1
                        else (
                            ["left", "right"]
                            if len(streams) == 2
                            else [f"s{i+1}" for i in range(len(streams))]
                        )
                    )
                    streams = [
                        {"id": ids[i], "items": s} for i, s in enumerate(streams)
                    ]
                # Else: assume object/variable-bearing structure; pass through untouched.
        except Exception:
            # If anything odd, pass `streams` through as-is
            pass

        super().__init__(locals(), side_effects)

    # ---- SweetBean hooks ----

    def _add_special_param(self):
        # Mirror SweetBean `duration` → jsPsych `trial_duration`
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

        # Map convenience alias end_on_response -> response_ends_trial
        try:
            if "end_on_response" in self.arg_js:
                self.arg_js["response_ends_trial"] = bool(
                    self.arg_js["end_on_response"]
                )
        except Exception:
            pass

        # Auto stream_order if classic bilateral row and not explicitly set
        try:
            streams = self.arg_js.get("streams") or []
            if (
                (not self.arg_js.get("stream_order"))
                and self.arg_js.get("direction", "row") == "row"
                and isinstance(streams, list)
                and len(streams) == 2
            ):
                a, b = (streams[0] or {}).get("id"), (streams[1] or {}).get("id")
                if a and b:
                    self.arg_js["stream_order"] = f"{a},{b}"
        except Exception:
            pass

        # If any distractor lacks index AND there is exactly one target, copy target's index
        try:
            tlist = self.arg_js.get("targets") or []
            dlist = self.arg_js.get("distractors") or []
            if (
                isinstance(tlist, list)
                and len(tlist) == 1
                and isinstance(dlist, list)
                and len(dlist) > 0
            ):
                t_idx = tlist[0].get("index", None)
                for d in dlist:
                    if "index" not in d or d.get("index") in (None, "null"):
                        d[
                            "index"
                        ] = t_idx  # copy as-is (works for ints or variable placeholders)
                self.arg_js["distractors"] = dlist
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
        pass

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError


class BilateralRSVP(_BaseStimulus):
    """
    Simple bilateral wrapper for your dedicated plugin: window.jsPsychBilateralRsvp
    (plugin name: "rsvp-bilateral" / class var: jsPsychBilateralRsvp)

    API matches the TS plugin's `bilateralInfo.parameters` exactly and is intentionally
    smaller than `RSVP`. Use this when you only need two lateral streams and a single
    target (plus optional opposite-stream distractor).
    """

    type = "jsPsychBilateralRsvp"

    def __init__(
        self,
        left: Any,
        right: Any,
        *,
        # Target
        target_side: Union[str, Any] = "left",  # "left" | "right" | Variable
        target_index: Any = 0,  # int | Variable
        target_shape: Union[
            str, Any
        ] = "circle",  # "circle" | "square" | "underline" | "none" | Variable
        # Optional distractor (opposite stream)
        distractor_index: Optional[Any] = None,  # int | Variable
        distractor_shape: Optional[Union[str, Any]] = None,  # shape | Variable | None
        # Pass-through presentation/timing
        stimulus_duration: int = 100,
        isi: int = 0,
        choices: Union[str, List[str]] = "ALL",
        mask_html: Optional[str] = None,
        color: str = "#ffffff",
        background: str = "#000000",
        token_box_size: str = "18vmin",
        token_font_size: str = "10vmin",
        token_padding: str = "0.25em 0.45em",
        trial_duration: Optional[int] = None,
        # SweetBean generic
        duration: Optional[int] = None,
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            left:
                Per-trial items for the left stream (e.g., ["O","Q","O",...]) or a
                Variable (FunctionVariable / TimelineVariable / DataVariable) that
                evaluates to such a list.
            right:
                Per-trial items for the right stream or a Variable producing a list.

            target_side:
                "left" or "right". Which stream contains the target. Default "left".
            target_index:
                Zero-based index of the target within the chosen stream. May be an int
                or a Variable. Default 0.
            target_shape:
                Decoration for the target: "circle" | "square" | "underline" | "none".
                Default "circle".

            distractor_index:
                Optional zero-based index for an opposite-stream distractor. If either
                `distractor_index` or `distractor_shape` is supplied, a distractor entry is
                created on the stream opposite to `target_side`. If `distractor_index`
                is omitted, it defaults to `target_index`.
            distractor_shape:
                Optional decoration shape for the distractor ("circle" | "square" |
                "underline" | "none"). If None, the shape is not overridden (plugin
                defaults apply).

            stimulus_duration:
                Milliseconds each token is displayed. Default 100.
            isi:
                Inter-stimulus interval (ms) between tokens. Default 0.
            choices:
                "ALL", "NO_KEYS", or list[str] of valid keys. Default "ALL".
            mask_html:
                Optional HTML mask shown between tokens. Default None.
            color:
                Default text/border color. Default "#ffffff".
            background:
                Background color. Default "#000000".
            token_box_size:
                CSS size for the fixed token box. Default "18vmin".
            token_font_size:
                CSS font size for token glyphs. Default "10vmin".
            token_padding:
                CSS padding inside decoration outlines. Default "0.25em 0.45em".
            trial_duration:
                Optional hard stop (ms). Default None.

            duration:
                SweetBean convenience alias; mirrored into `trial_duration` if set.
            side_effects:
                Optional dictionary of side effects to pass along.

        Notes:
            - This is a thin wrapper that forwards to the underlying `Rsvp` implementation
              with a simpler two-stream interface.
            - If you need multiple targets, per-target response windows, or more complex
              layouts, use `RSVP` instead.
        """
        # We do NOT normalize left/right (could be Variables).
        # Ensure lists at runtime in your mapping.
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        # Mirror SweetBean `duration` → jsPsych `trial_duration`
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

    def _process_response(self):
        # The underlying Rsvp implementation (invoked by the bilateral wrapper)
        # provides key_press and rt in its data. Add SweetBean convenience fields:
        self.js_data += 'data["bean_key"] = data["key_press"];'
        self.js_data += 'data["bean_rt"] = data["rt"];'
        self.js_data += (
            'data["bean_any_hit"] = '
            '(Array.isArray(data["targets"]) && data["targets"].some(t => t.hit));'
        )

    def _set_before(self):
        pass

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError
