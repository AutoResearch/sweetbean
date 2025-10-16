# sweetbean/stimulus/GaborArray.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus
from sweetbean.variable import TimelineVariable


class Gabor(_BaseStimulus):
    """
    Procedural Gabor patch renderer (wraps @sweet-jspsych/plugin-gabor-array).

    Core idea:
      - Draw one or more Gabor patches on a canvas and collect keyboard/mouse
        responses. Geometry is pixel-based by default; pass px_per_deg to use
        degree-based parameters.

    Patch spec (each element of `patches`):
      - x_px, y_px            : float  (center position relative to canvas center, px)
      - sigma_px              : float  (Gaussian sigma in px)
        OR sigma_deg          : float  (sigma in degrees; requires px_per_deg)
      - orientation_deg       : float  [0..180)
      - contrast              : float  [0..1]
      - sf_cpp                : float  cycles per pixel
        OR sf_cpd             : float  cycles per degree; requires px_per_deg
      - phase_deg             : float  [0..360)
      - size_px               : int    (square draw size; default ≈ 6·sigma)
      - label                 : str    (optional tag included in data)

    Responses:
      - Keyboard: map keys either implicitly (ArrowLeft/Right → leftmost/rightmost patch)
        or explicitly via keymap_to_patch_index (e.g., {"f":0, "j":1}).
      - Mouse: click selects the nearest patch center (if allow_mouse=True).

    Notes:
      - In the browser bundle, the plugin exposes a global constructor:
        `window.jsPsychGaborArray`. This class keeps `type` as that string so
        SweetBean emits a declarative config and lets the shim swap in the constructor.
    """

    # Keep a string so the emitted JS config stays declarative.
    # The browser bundle (IIFE) must set window.jsPsychGaborArray = PluginClass
    type = "jsPsychGaborArray"

    def __init__(
        self,
        # Stimulus content
        patches: Optional[Union[List[Dict[str, Any]], TimelineVariable]] = None,
        # Canvas & photometry
        canvas_width: int = 800,
        canvas_height: int = 600,
        bg_gray: float = 0.5,  # mean luminance in [0..1]
        px_per_deg: Optional[float] = None,  # enables deg-based params
        gamma: float = 1.0,  # 1.0 = no gamma correction
        # Timing
        trial_duration: Optional[int] = None,  # ms; None = no forced timeout
        timeout_ms: Optional[int] = None,  # alias; wins over trial_duration if set
        end_on_response: bool = True,
        # Responses
        response_keys: Optional[List[str]] = None,  # default handled in plugin
        allow_mouse: bool = True,
        keymap_to_patch_index: Optional[Dict[str, int]] = None,
        # SweetBean conveniences
        duration: Optional[
            int
        ] = None,  # alias for trial_duration (consistent with RSVP)
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            patches (list[dict] | TimelineVariable | None):
                The Gabor patch specification for this trial. Accepts either a
                concrete list or a TimelineVariable that evaluates per trial to a
                list. Each patch dict supports:

                  Required geometry/appearance
                  - x_px (float): X center in pixels, relative to canvas center.
                  - y_px (float): Y center in pixels, relative to canvas center.
                  - orientation_deg (float): Orientation in degrees [0..180).
                  - contrast (float): Michelson contrast in [0..1].
                  - phase_deg (float): Phase in degrees [0..360).

                  Spatial frequency (choose one)
                  - sf_cpp (float): Cycles per pixel, OR
                  - sf_cpd (float): Cycles per degree (requires px_per_deg).

                  Gaussian size (choose one)
                  - sigma_px (float): Sigma in pixels, OR
                  - sigma_deg (float): Sigma in degrees (requires px_per_deg).

                  Optional
                  - size_px (int): Square draw size in px (defaults to ~6*sigma_px).
                  - label (str): Arbitrary tag copied to data.

                Example single patch:
                {
                    "x_px": 0.0, "y_px": 0.0,
                    "orientation_deg": 45, "contrast": 0.5, "phase_deg": 0,
                    "sf_cpd": 3.0,   # uses px_per_deg if provided
                    "sigma_deg": 0.4 # uses px_per_deg if provided
                }

            canvas_width (int):
                Canvas width in pixels. Default 800.
            canvas_height (int):
                Canvas height in pixels. Default 600.
            bg_gray (float):
                Mean background luminance in [0..1]. Default 0.5.
            px_per_deg (float | None):
                Pixels per degree for converting *deg* fields (sigma_deg, sf_cpd)
                to pixels. If None, deg-based fields are not allowed. Default None.
            gamma (float):
                Gamma correction factor for display (1.0 = no correction). Default 1.0.

            trial_duration (int | None):
                Hard timeout (ms) for the trial. None = no forced timeout. Default None.
            timeout_ms (int | None):
                Alias for trial_duration; if set, this takes precedence. Default None.
            end_on_response (bool):
                If True, end the trial immediately after a valid response. Default True.

            response_keys (list[str] | None):
                Allowed keys. If None, defaults to ["ArrowLeft", "ArrowRight"] to
                match the plugin’s default. Keys can be remapped with
                keymap_to_patch_index.
            allow_mouse (bool):
                If True, clicking selects the nearest patch center. Default True.
            keymap_to_patch_index (dict[str, int] | None):
                Optional explicit key→patch index map (e.g., {"f":0, "j":1}).
                If omitted, the plugin can infer a side-based mapping for arrow keys.

            duration (int | None):
                SweetBean convenience alias mirrored to `trial_duration` during build.
                If provided, `trial_duration` is set to this value. Default None.
            side_effects (dict | None):
                Optional side-effect configuration passed to the runtime.

        Emits (added to jsPsych data):
            - bean_rt (number | None): Reaction time in ms.
            - bean_resp_key (str | None): Key pressed, if any.
            - bean_resp_side (str | None): Side label derived by the plugin, if any.
            - bean_chosen_patch (int | None): Selected patch index (0-based).
            - bean_n_patches (int): Number of patches rendered.
            - bean_patches (list[dict]): Patch descriptors used on this trial.
            - bean_onset_ms / bean_offset_ms (number | None): Timing markers.

        Notes:
            - Provide either pixel- or degree-based size/frequency per patch
              (sigma_px vs sigma_deg, sf_cpp vs sf_cpd). Degree-based fields require
              `px_per_deg` to be set.
            - Use TimelineVariable("patches") if patches vary per trial.
            - If both `duration` and `trial_duration` are given, `duration` is copied
              into `trial_duration` (matching other SweetBean stimuli).
            - Null/None optionals are dropped to let the plugin use its internal defaults.

        Example:
            from sweetbean import Block, Experiment
            from sweetbean.variable import TimelineVariable
            timeline = [
                {
                    "patches": [
                        {
                            "x_px": -150, "y_px": 0,
                            "orientation_deg": 30, "contrast": 0.6, "phase_deg": 0,
                            "sf_cpd": 2.5, "sigma_deg": 0.3,  # requires px_per_deg
                            "label": "left"
                        },
                        {
                            "x_px": 150, "y_px": 0,
                            "orientation_deg": 120, "contrast": 0.6, "phase_deg": 90,
                            "sf_cpd": 2.5, "sigma_deg": 0.3,
                            "label": "right"
                        },
                    ]
                }
            ]
            stim = Gabor(
                patches=TimelineVariable("patches"),
                canvas_width=800, canvas_height=600,
                bg_gray=0.5, px_per_deg=40.0, gamma=1.0,
                trial_duration=None, end_on_response=True,
                response_keys=["f","j"],
                keymap_to_patch_index={"f":0, "j":1},
            )
            block = Block([stim], timeline=timeline)
            Experiment([block]).to_html("gabor.html")
        """

        if patches is None:
            patches = []

        # Default keys if user didn't provide any; match plugin default
        if response_keys is None:
            response_keys = ["ArrowLeft", "ArrowRight"]

        super().__init__(locals(), side_effects)

    # ---- SweetBean hooks ----

    def _add_special_param(self):
        """
        - Map SweetBean `duration` to jsPsych `trial_duration`.
        - Drop null-ish optionals so the plugin falls back to its defaults cleanly.
        - Keep a string `type` so the browser can resolve it to the actual constructor.
        """
        arg = self.arg_js

        # Alias duration → trial_duration
        if arg.get("duration") not in (None, "null"):
            arg["trial_duration"] = arg["duration"]

        # Remove None/null fields (plugin has its own defaults)
        for k in (
            "px_per_deg",
            "trial_duration",
            "timeout_ms",
            "keymap_to_patch_index",
            "response_keys",
        ):
            if arg.get(k) in (None, "null"):
                arg.pop(k, None)

        # Ensure patches exists (empty list is fine)
        if arg.get("patches") is None:
            arg["patches"] = []

        # Keep declarative type so the IIFE shim can replace it at runtime
        arg["type"] = self.type

    def _process_response(self):
        """
        Mirror common fields into bean_* for convenience:
          - bean_rt
          - bean_resp_key
          - bean_resp_side
          - bean_chosen_patch
          - bean_n_patches
          - bean_patches (array of patch descriptors: x_px, y_px, sigma_px, sf_cpp, etc.)
          - bean_onset_ms / bean_offset_ms
        """
        self.js_data += 'data["bean_rt"] = data["rt"];'
        self.js_data += 'data["bean_resp_key"] = data["resp_key"];'
        self.js_data += 'data["bean_resp_side"] = data["resp_side"];'
        self.js_data += 'data["bean_chosen_patch"] = data["chosen_patch_index"];'
        self.js_data += 'data["bean_n_patches"] = data["n_patches"];'
        self.js_data += 'data["bean_patches"] = data["patches"];'
        self.js_data += 'data["bean_onset_ms"] = data["onset_ms"];'
        self.js_data += 'data["bean_offset_ms"] = data["offset_ms"];'

    def _set_before(self):
        # No extra on_load code required.
        pass

    # Language mode not supported
    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError
