from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus

Var = Any
IntLike = Union[int, Var]
StrLike = Union[str, Var]
StrListLike = Union[List[StrLike], Var]
BoolLike = Union[bool, Var]


class Symbol(_BaseStimulus):
    """
    SweetBean wrapper for window.jsPsychSymbol (string type: "symbol").

    Minimal + safe conveniences:
      - Pass `items` (list[dict] or Var) directly, OR provide a top-level `shape`
        to spawn a single-item list.
      - Top-level `color`/`texture` broadcast to items that haven't set their own
        (only when items is a concrete list).
      - If `items` is a Variable (TimelineVariable, FunctionVariable, etc.), it is
        forwarded unchanged and no expansion/broadcast is attempted
        (to avoid incorrect compile-time assumptions).

    Python API (snake_case) -> plugin (camelCase):
      canvas_width -> canvasWidth
      canvas_height -> canvasHeight
      background -> background
      items -> items
      duration -> trialDuration
      response_ends_trial -> responseEndsTrial
      choices -> choices
      allow_mouse -> allowMouse
    """

    type = "jsPsychSymbol"

    def __init__(
        self,
        *,
        # ---- Display ----
        canvas_width: IntLike = 800,
        canvas_height: IntLike = 600,
        background: StrLike = "transparent",
        # ---- Content ----
        items: Optional[Any] = None,  # list[dict] | Var
        shape: Optional[
            StrLike
        ] = None,  # fast path for a single item (only if concrete)
        color: Optional[StrLike] = None,  # optional broadcast (concrete lists only)
        texture: Optional[Any] = None,  # optional broadcast (concrete lists only)
        # ---- Timing / responses ----
        duration: Optional[IntLike] = None,
        response_ends_trial: BoolLike = True,
        choices: Optional[Union[StrLike, StrListLike]] = None,
        allow_mouse: BoolLike = False,
        # ---- Scoring convenience ----
        correct_key: Optional[StrLike] = None,
        # ---- SweetBean generic ----
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            canvas_width (int): Canvas width in px. Default 800.
            canvas_height (int): Canvas height in px. Default 600.
            background (str): Page background CSS color. Default "transparent".

            items (list[dict] | None):
                List of shape dicts. Each item supports:

                  Required
                  - shape: one of
                      "circle" | "ring" | "rectangle" | "triangle" | "cross"

                  Size (by shape)
                  - circle    : radius (int)
                  - ring      : innerRadius (int), outerRadius (int)
                  - rectangle : width (int), height (int), cornerRadius (int, opt)
                  - triangle  : side (int)
                  - cross     : armLen (int), armWidth (int)

                  Common (optional)
                  - x, y      : int. Position in px relative to center (default 0,0)
                  - z         : int. Draw order; higher draws later (default 0)
                  - rotation  : float deg, clockwise from vertical (default 0)
                  - alpha     : float 0..1 (default 1)
                  - blend     : canvas comp-op string. One of:
                                 "source-over","lighter","multiply","screen",
                                 "overlay","darken","lighten","difference",
                                 "exclusion","hard-light","soft-light"
                  - color     : CSS color string; used if no texture (default "#000")
                  - texture   : dict (see Texture below)
                  - stroke    : CSS color string (outline). Optional.
                  - strokePx  : int stroke width (px). Optional.

            shape (str | None):
                Fast path. If set and `items` is empty/None, creates a single
                item {"shape": shape}. Useful for one-off trials.

            color (str | None):
                Broadcast fill color to any item that lacks "color".
                Also applied to the fast-path single item.

            texture (dict | None):
                Broadcast texture to any item that lacks "texture".
                Also applied to the fast-path single item.

            duration (int | None):
                Trial timeout in ms. Mapped to plugin key `trialDuration`.

            response_ends_trial (bool): If True, end on first valid response.

            choices (list[str] | str | None):
                Allowed keys. None/""/"NO_KEYS" → []; "ALL"/"ALL_KEYS" → "ALL_KEYS";
                a single string becomes [that string].

            allow_mouse (bool): If True, mouse click counts as a response.

            correct_key (str | None): Copied into data; enables simple correctness.

            side_effects (dict | None): SweetBean side-effects configuration.

            Texture:
                A texture is a dict with a "type" and type-specific fields.

                - type: "stripes"
                  Fields:
                    bar    : int period in px (stripe A + stripe B). Default 20.
                    duty   : float 0..1 fraction for stripe A. Default 0.5.
                    angle  : float deg; extra rotation added to item.rotation. Default 0.
                    phase  : int px shift along stripe normal. Default 0.
                    colors : [str, str] optional two-color palette. If omitted, a
                             light/dark pair is derived from the item "color".

                - type: "noise"
                  Fields:
                    cell   : int size of each block in px. Default 4.
                    seed   : int optional RNG seed.
                    colors : [str, str] optional two-color palette. If omitted, a
                             light/dark pair is derived from the item "color".
                    mix    : float 0..1 mean toward second color. Default 0.5.
        """
        # ---------------- items construction / broadcasting ----------------
        items_final: Any = items

        # Heuristic for "variable-like": we only treat as concrete when it's a Python list of dicts
        is_concrete_list = isinstance(items_final, list) and all(
            isinstance(it, dict) for it in items_final
        )
        is_empty_or_none = (items_final is None) or (
            isinstance(items_final, list) and len(items_final) == 0
        )

        # Single-item fast path ONLY when shape is a concrete string and items isn't provided
        if is_empty_or_none and isinstance(shape, str) and shape.strip():
            one: Dict[str, Any] = {"shape": shape.strip()}
            if color not in (None, "null"):
                one["color"] = color
            if texture not in (None, "null"):
                one["texture"] = texture
            items_final = [one]
            is_concrete_list = True

        # Broadcast top-level color/texture ONLY when we truly have a concrete list
        if is_concrete_list and (
            color not in (None, "null") or texture not in (None, "null")
        ):
            out: List[Dict[str, Any]] = []
            for it in items_final:  # type: ignore[iteration-over-optional]
                tmp = dict(it)
                # Add color only if item doesn't specify it
                if color not in (None, "null") and ("color" not in tmp):
                    tmp["color"] = color
                # Add texture only if item doesn't specify it
                if texture not in (None, "null") and ("texture" not in tmp):
                    tmp["texture"] = texture
                out.append(tmp)
            items_final = out

        # ---------------- choices normalization (keep Vars untouched) ----------------
        choices_final: Any = choices
        if not hasattr(choices, "__dict__") and not callable(choices):
            if choices in (None, "NO_KEYS", "no_keys", "", []):
                choices_final = []
            elif isinstance(choices, str):
                s = choices.strip()
                choices_final = "ALL_KEYS" if s.lower() in ("all", "all_keys") else [s]
            elif isinstance(choices, list):
                choices_final = choices

        # ---------------- build params for plugin ----------------
        params: Dict[str, Any] = {
            "canvasWidth": canvas_width,
            "canvasHeight": canvas_height,
            "background": background,
            "items": items_final,
            "trialDuration": duration,  # single source of truth
            "responseEndsTrial": response_ends_trial,
            "choices": choices_final,
            "allowMouse": allow_mouse,
            # pass-through for scoring convenience (not a plugin param)
            "correct_key": correct_key,
        }

        super().__init__(params, side_effects)

    # ---- SweetBean hooks -------------------------------------------------

    def _add_special_param(self):
        # ensure correct_key is included in trial data if provided
        ck = self.arg_js.get("correct_key", None)
        if ck not in (None, "null"):
            self.arg_js.setdefault("data", {})
            self.arg_js["data"]["correct_key"] = ck

    def _process_response(self):
        # mirror core timing/response fields for convenience
        self.js_data += 'data["bean_key"] = data["resp_key"];'
        self.js_data += 'data["bean_rt"] = data["rt"];'
        self.js_data += 'data["bean_onset"] = data["onset_ms"];'
        self.js_data += 'data["bean_offset"] = data["offset_ms"];'
        self.js_data += 'data["bean_n_items"] = data["n_items"];'
        # optional correctness if a correct_key was supplied
        self.js_data += (
            'if (typeof data["correct_key"] !== "undefined" && data["correct_key"] !== null) {'
            '  var rk = (data["resp_key"] == null) ? null : String(data["resp_key"]).toLowerCase();'
            '  var ck = String(data["correct_key"]).toLowerCase();'
            '  data["bean_correct"] = (rk !== null && rk === ck);'
            "}"
        )

    def _set_before(self):
        pass

    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError
