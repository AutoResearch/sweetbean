from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus

# ----------------------------------------------------------------------
# Type helpers so Variables (TimelineVariable / FunctionVariable / etc.)
# are accepted anywhere a scalar or list is expected.
# ----------------------------------------------------------------------
Var = Any
IntLike = Union[int, Var]
StrLike = Union[str, Var]
IntListLike = Union[List[IntLike], Var]
StrListLike = Union[List[StrLike], Var]
CssLike = Union[str, Var]
HtmlLike = Union[str, Var]
BoolLike = Union[bool, Var]


class RSVP(_BaseStimulus):
    """
    General RSVP wrapper for your jsPsych plugin: window.jsPsychRsvp
    (plugin name: "rsvp" / class var: jsPsychRsvp)

    Streams are **pure content** (letters/digits). All shapes/colors/HTML wrapping
    are specified via target/distractor parameters (explicit arrays OR convenience
    arrays that accept scalars/lists/Variables and are broadcast by the plugin).

    No short-form normalization is performed here—Variables pass through untouched.
    """

    type = "jsPsychRsvp"

    def __init__(
        self,
        # ---------------- Appearance / layout ----------------
        background: CssLike = "#000000",
        color: CssLike = "#ffffff",
        direction: StrLike = "row",  # "row" | "column"
        stream_order: Optional[StrLike] = None,  # e.g., "left,right"
        gap: CssLike = "6rem",
        # ---------------- Token sizing ----------------
        token_box_size: CssLike = "18vmin",  # fixed square box
        token_font_size: CssLike = "10vmin",  # glyph size
        token_padding: CssLike = "0.25em 0.45em",  # inner padding for outlines
        # ---------------- Streams & timing ----------------
        streams: Optional[List[Any]] = None,  # preferred: [{"id":..., "items":[...]}]
        stimulus_duration: IntLike = 100,  # ms each token is shown
        isi: IntLike = 0,  # ms between tokens (SOA = dur + isi)
        mask_html: Optional[HtmlLike] = None,  # HTML shown during ISI (e.g., "•")
        # ---------------- Responses ----------------
        choices: Union[StrLike, List[StrLike]] = "ALL",  # "ALL" | "NO_KEYS" | ["f","j"]
        end_on_response: BoolLike = False,  # convenience → response_ends_trial
        response_window: Optional[IntLike] = None,  # ms; None = unlimited
        correct_keys: Optional[StrLike] = None,  # e.g., "f,j" for scoring
        # ---------------- Targets (timing + decoration) ----------------
        decorate_targets: BoolLike = True,  # show decoration if shape != "none"
        target_shape: StrLike = "none",  # default shape if per-target omits
        target_stroke: CssLike = "3px",  # outline/underline thickness
        targets: Optional[
            List[Dict[str, Any]]
        ] = None,  # explicit array [{stream_id, index, ...}]
        # Convenience (scalars OR lists OR Variables) — broadcast by plugin:
        target_index: Optional[
            Union[IntLike, IntListLike]
        ] = None,  # number | [number|Var,...]
        target_side: Optional[
            Union[StrLike, StrListLike]
        ] = None,  # stream ids ("left"/"right"/custom)
        target_color: Optional[
            Union[CssLike, List[CssLike], Var]
        ] = None,  # CSS color; with shape:"none" colors text
        target_html: Optional[
            Union[HtmlLike, List[HtmlLike], Var]
        ] = None,  # HTML template or full override
        # ---------------- Distractors (decoration only) ----------------
        decorate_distractors: BoolLike = False,
        distractor_shape: StrLike = "none",
        distractor_color: CssLike = "#888888",
        distractor_stroke: CssLike = "2px",
        distractors: Optional[List[Dict[str, Any]]] = None,  # explicit array
        # Convenience (scalars OR lists OR Variables) — broadcast by plugin:
        distractor_index: Optional[Union[IntLike, IntListLike]] = None,
        distractor_side: Optional[Union[StrLike, StrListLike]] = None,  # stream ids
        distractor_color2: Optional[
            Union[CssLike, List[CssLike], Var]
        ] = None,  # per-item override (else distractor_color)
        distractor_html: Optional[
            Union[HtmlLike, List[HtmlLike], Var]
        ] = None,  # HTML template or full override
        # ---------------- Lifetime & data ----------------
        trial_duration: Optional[
            IntLike
        ] = None,  # hard stop; else ends after last token
        record_timestamps: BoolLike = True,  # include per-token onset/offset in data["schedule"]
        # ---------------- SweetBean generic ----------------
        duration: Optional[IntLike] = None,  # alias mirrored into trial_duration
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        background : CSS color | Variable
            Background color for the RSVP screen (e.g., "#000", "black").
        color : CSS color | Variable
            Default text/border color (used when a per-item color is not provided).
        direction : {"row","column"} | Variable
            Layout of streams (left–right for "row", top–bottom for "column").
        stream_order : str | None | Variable
            Comma-separated DOM order of stream IDs (e.g., "left,right").
            If omitted and there are exactly two streams with row layout, it is
            auto-filled from the two stream IDs (e.g., "left,right").
        gap : CSS length | Variable
            Gap between streams in non-bilateral layouts.

        token_box_size : CSS length | Variable
            Size of the fixed token box (prevents wobble when borders appear).
        token_font_size : CSS length | Variable
            Font size for the glyphs inside each token box.
        token_padding : CSS length | Variable
            Inner padding used by outlined/underlined shapes.

        streams : list | Variable
            Per-trial stream specs. Prefer object form:
              [{"id":"left","items":["O","Q",...]}, {"id":"right","items":["1","2",...]}]
            Streams are **pure content**; do NOT embed "circle"/"square"/colors here.

        stimulus_duration : int | Variable
            Milliseconds each token is displayed.
        isi : int | Variable
            Inter-stimulus interval (ms) between tokens.
        mask_html : str | None | Variable
            Optional HTML shown during the ISI (e.g., "•").

        choices : "ALL" | "NO_KEYS" | list[str] | Variable
            Allowed keys during RSVP. Use "NO_KEYS" when you collect responses afterward.
        end_on_response : bool | Variable
            If True, RSVP ends immediately after the first valid keypress
            (mapped to plugin's `response_ends_trial`).
        response_window : int | None | Variable
            Time window (ms) for scoring target hits; None = unlimited.
        correct_keys : str | None | Variable
            Comma-separated keys used for per-target hit scoring (optional).

        decorate_targets : bool | Variable
            Whether to render target decorations (ignored if shape == "none").
        target_shape : {"circle","square","underline","none"} | Variable
            Default shape if a target omits its own shape.
        target_stroke : CSS length | Variable
            Outline/underline thickness for targets.
        targets : list[dict] | None
            Explicit target list. Each item may include:
              stream_id, index, label, response_window, correct_keys,
              shape, color, stroke, padding, html, style, className.

        target_index : int | list[int|Variable] | Variable
            Convenience form—position(s) of target(s) in their streams.
        target_side : str | list[str|Variable] | Variable
            Convenience—stream id(s) (e.g., "left"/"right"/custom ids).
        target_color : CSS color | list | Variable
            Per-item color. If the item's shape is "none", this colors the glyph itself.
        target_html : str (template) | list[str] | Variable
            Per-item HTML. If it contains {{content}} or {CONTENT}, the stream item’s
            text is injected; otherwise treated as full override.

        decorate_distractors : bool | Variable
            Whether to render distractor decorations.
        distractor_shape : {"circle","square","underline","none"} | Variable
            Default shape for distractors that omit a shape.
        distractor_color : CSS color | Variable
            Default distractor color (border or underline; or glyph if shape == "none").
        distractor_stroke : CSS length | Variable
            Outline/underline thickness for distractors.
        distractors : list[dict] | None
            Explicit distractor list. Each item may include:
              stream_id, index, label, shape, color, stroke, padding, html, style, className.

        distractor_index : int | list[int|Variable] | Variable
            Convenience—position(s) of distractor(s).
        distractor_side : str | list[str|Variable] | Variable
            Convenience—stream id(s) for distractor(s).
        distractor_color2 : CSS color | list | Variable
            Per-item color override (falls back to `distractor_color` if not set).
        distractor_html : str (template) | list[str] | Variable
            Per-item HTML for distractors (same templating as target_html).

        trial_duration : int | None | Variable
            Hard stop (ms). If None, the trial ends after the last token (+ ISI).
        record_timestamps : bool | Variable
            If True, includes per-token onsets/offsets in data["schedule"].

        duration : int | None | Variable
            SweetBean alias mirrored into `trial_duration`.
        side_effects : dict | None
            Optional side effects passed along at runtime.
        """
        if streams is None:
            streams = []
        if targets is None:
            targets = []
        if distractors is None:
            distractors = []
        if distractor_index is None and distractors is None:
            distractor_index = target_index

        # ⛔️ Do NOT normalize/transform streams here—must support Variables unchanged.
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

        # Auto stream_order if exactly two streams in row layout and not explicitly set
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
                        d["index"] = t_idx
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
    Two-stream (left/right) wrapper around window.jsPsychBilateralRsvp.
    You provide left/right item lists (or Variables). The wrapper composes
    targets/distractors using convenience arrays (scalars/lists/Variables) and
    delegates to the base RSVP plugin.

    Streams are **pure content**; all decoration/color/HTML is via params.
    """

    type = "jsPsychBilateralRsvp"

    def __init__(
        self,
        # ---------------- Content ----------------
        left: Any,
        right: Any,
        # ---------------- Targets (scalars OR lists OR Variables) ----------------
        target_side: Optional[Union[StrLike, StrListLike]] = "left",  # "left" | "right"
        target_index: Optional[Union[IntLike, IntListLike]] = 0,
        target_shape: Optional[
            Union[StrLike, StrListLike]
        ] = "circle",  # "circle"|"square"|"underline"|"none"
        target_color: Optional[Union[CssLike, List[CssLike], Var]] = None,
        target_html: Optional[Union[HtmlLike, List[HtmlLike], Var]] = None,
        # ---------------- Distractors (scalars OR lists OR Variables) ----------------
        distractor_index: Optional[Union[IntLike, IntListLike]] = None,
        distractor_side: Optional[
            Union[StrLike, StrListLike]
        ] = None,  # if omitted, plugin infers opposite of target_side
        distractor_shape: Optional[Union[StrLike, StrListLike]] = None,
        distractor_color: Optional[Union[CssLike, List[CssLike], Var]] = None,
        distractor_html: Optional[Union[HtmlLike, List[HtmlLike], Var]] = None,
        # ---------------- Presentation/timing ----------------
        stimulus_duration: IntLike = 100,
        isi: IntLike = 0,
        choices: Union[StrLike, List[StrLike]] = "ALL",
        mask_html: Optional[HtmlLike] = None,
        color: CssLike = "#ffffff",
        background: CssLike = "#000000",
        token_box_size: CssLike = "18vmin",
        token_font_size: CssLike = "10vmin",
        token_padding: CssLike = "0.25em 0.45em",
        trial_duration: Optional[IntLike] = None,
        # ---------------- Convenience ----------------
        end_on_response: BoolLike = False,  # maps to response_ends_trial in underlying plugin
        # ---------------- SweetBean generic ----------------
        duration: Optional[IntLike] = None,
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        left, right : list | Variable
            Content lists for the left/right streams (e.g., ["O","Q","O",...]).
            May be Variables that evaluate to such lists.

        target_side : "left" | "right" | list[...] | Variable
            Side(s) containing the target(s). Lists broadcast with other target_* arrays.
        target_index : int | list[int|Variable] | Variable
            Index/indices of target(s) within the chosen stream(s).
        target_shape : {"circle","square","underline","none"} | list[...] | Variable
            Per-item decoration; "none" means color-only (no outline).
        target_color : CSS color | list[...] | Variable
            Per-item color (glyph color when shape == "none"; else border/underline color).
        target_html : str (template or full HTML) | list[...] | Variable
            If includes {{content}} / {CONTENT}, wraps the stream glyph; otherwise full override.

        distractor_index : int | list[int|Variable] | Variable
            Index/indices of distractor(s). If omitted and you set target_index,
            Bilateral defaults to the same index as each target (per-item).
        distractor_side : "left" | "right" | list[...] | Variable
            Side(s) for distractor(s). If omitted and target_side is provided,
            Bilateral infers the **opposite** side for each item.
        distractor_shape : {"circle","square","underline","none"} | list[...] | Variable
            Per-item distractor decoration.
        distractor_color : CSS color | list[...] | Variable
            Per-item distractor color (glyph if shape=="none"; else border/underline).
        distractor_html : str (template/full) | list[...] | Variable
            Per-item HTML for distractors (same templating as targets).

        stimulus_duration : int | Variable
            Milliseconds each token is displayed.
        isi : int | Variable
            Inter-stimulus interval (ms) between tokens.
        choices : "ALL" | "NO_KEYS" | list[str] | Variable
            Allowed keys during RSVP. Use "NO_KEYS" when collecting responses afterward.
        mask_html : str | None | Variable
            HTML mask shown during ISI (e.g., "•").
        color, background, token_box_size, token_font_size, token_padding : CSS | Variable
            Visual defaults passed through to the underlying RSVP plugin.
        trial_duration : int | None | Variable
            Hard stop for the RSVP (ms).

        end_on_response : bool | Variable
            Convenience; maps to the underlying plugin’s `response_ends_trial`.

        duration : int | None | Variable
            SweetBean alias mirrored into `trial_duration`.
        side_effects :
            Optional side-effect configuration passed to the runtime. This expects
                a list of SideEffect definitions (see SweetBean docs) which can be
                used to update global data like overall score or trial counter.
        """
        super().__init__(locals(), side_effects)

    def _add_special_param(self):
        # Mirror SweetBean `duration` → jsPsych `trial_duration`
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

        # Map convenience alias end_on_response -> response_ends_trial (passed through)
        try:
            if "end_on_response" in self.arg_js:
                self.arg_js["response_ends_trial"] = bool(
                    self.arg_js["end_on_response"]
                )
        except Exception:
            pass

    def _process_response(self):
        # The underlying RSVP provides key_press/rt; add SweetBean convenience fields:
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
