from typing import Any, Dict, List, Optional, Union

from sweetbean.stimulus.Stimulus import _BaseStimulus
from sweetbean.variable import TimelineVariable


class Foraging(_BaseStimulus):
    """
    Visual Foraging stimulus (wraps @sweet-jspsych/plugin-foraging)

    Arrays-only API:
      - targets:     list[ItemSpec]
      - distractors: list[ItemSpec]

    ItemSpec fields (each item defines ONE of {html|text|shape|src}, plus options):
      - html: str
      - text: str
      - shape: Literal["circle","square","triangle"]
      - src: str
      - color: str                      # overrides overlay_pool sampling
      - rotationDeg: int                # overrides rotation_pool sampling
      - pos: dict                       # {mode:"abs"|"grid"|"circle", ...}
      - size: str                       # e.g., "12vmin"
      - fontSize: str
      - id: str
      - attrs: dict[str,str]

    Notes:
      - By default, randomized non-overlapping placement in a centered square arena.
      - Trial ends when all targets found unless you change `end_when_found=False`
        or set an explicit `trial_duration`.
    """

    # IMPORTANT: For SweetBean, keep a string "type" so SweetBean emits
    # a declarative config object. The browser bundle must set window.jsPsychForaging.
    type = "jsPsychForaging"

    def __init__(
        self,
        # Required-ish (can be empty)
        targets: Optional[Union[List[Dict[str, Any]], TimelineVariable]] = None,
        distractors: Optional[Union[List[Dict[str, Any]], TimelineVariable]] = None,
        # Layout & placement
        position_mode: str = "random",  # "random" | "grid" | "circle"
        grid_cols: Optional[int] = None,
        grid_rows: Optional[int] = None,
        ring_radius_vmin: float = 30,
        randomize_positions: bool = True,  # grid/circle only
        # Arena & spacing
        arena_size_vmin: float = 92,  # centered square side (vmin)
        placement_inset_vmin: float = 6,  # inner margin
        min_gap_vmin: float = 2.5,  # extra pairwise gap
        # Visuals
        background: str = "#000000",  # default black
        color: str = "#ffffff",  # default foreground (text/border)
        token_box_size: str = "12vmin",
        token_font_size: str = "10vmin",
        # Pools (defaults are in the plugin too; pass to control sampling)
        overlay_pool: Optional[List[str]] = None,
        rotation_pool: Optional[List[int]] = None,
        # Timing & control
        trial_duration: Optional[
            int
        ] = None,  # None => ends when all targets found (if end_when_found=True)
        end_when_found: bool = True,
        response_ends_trial: bool = False,
        # Determinism
        seed: Optional[int] = None,
        # Feedback
        show_star_feedback: bool = False,  # OFF by default
        star_color: str = "#f6b500",
        # Hooks / triggers
        # Example: {"on_all_targets_collected": "end_trial"}
        triggers: Optional[Dict[str, Any]] = None,
        # SweetBean convenience
        duration: Optional[int] = None,  # mirrors RSVP: alias for trial_duration
        side_effects: Optional[Dict[str, Any]] = None,
    ):
        """
        Arguments:
            targets (list[dict] | TimelineVariable | None):
                Trial’s target items. Accepts a concrete list or a TimelineVariable
                that evaluates per trial to a list. Each item is an ItemSpec dict
                that defines exactly ONE of {html | text | shape | src} plus
                optional styling/placement fields:

                  Content (choose exactly one)
                  - html (str): Raw HTML.
                  - text (str): Plain text (rendered in a token box).
                  - shape (str): One of "circle", "square", "triangle".
                  - src (str): Image URL/path.

                  Optional appearance/identity
                  - color (str): CSS color; overrides overlay_pool sampling.
                  - rotationDeg (int): Rotation in degrees; overrides rotation_pool.
                  - size (str): CSS size of the token box (e.g., "12vmin").
                  - fontSize (str): For text content (e.g., "10vmin").
                  - id (str): Opaque label copied to data.
                  - attrs (dict[str,str]): Arbitrary HTML attributes.

                  Placement override (optional; else global placement rules apply)
                  - pos (dict): One of the following shapes:
                        {"mode": "abs", "x_vmin": <float>, "y_vmin": <float>}
                        {"mode": "grid", "row": <int>, "col": <int>}
                        {"mode": "circle", "angle_deg": <float>, "radius_vmin": <float>}

            distractors (list[dict] | TimelineVariable | None):
                Same ItemSpec structure as `targets`. May be empty.

            position_mode (str):
                Global placement policy when items don’t provide an explicit `pos`.
                One of "random" | "grid" | "circle". Default "random".
            grid_cols (int | None):
                Number of columns for "grid" placement. If None, inferred from count.
            grid_rows (int | None):
                Number of rows for "grid" placement. If None, inferred from count.
            ring_radius_vmin (float):
                Ring radius for "circle" placement, in vmin units. Default 30.
            randomize_positions (bool):
                If True, jitter positions within the grid cell / along the ring for
                "grid"/"circle" modes. Default True.

            arena_size_vmin (float):
                Side length (vmin) of the centered square arena. Default 92.
            placement_inset_vmin (float):
                Inner safety margin from arena edges. Default 6.
            min_gap_vmin (float):
                Extra minimum pairwise spacing between item centers. Default 2.5.

            background (str):
                Arena background color. Default "#000000".
            color (str):
                Default foreground color (text/borders). Default "#ffffff".
            token_box_size (str):
                Default token box size (CSS). Default "12vmin".
            token_font_size (str):
                Default font size for text tokens (CSS). Default "10vmin".

            overlay_pool (list[str] | None):
                Optional pool of overlay symbols/colors; sampled per item unless the
                ItemSpec provides an explicit `color`. Omit/None to use plugin defaults.
            rotation_pool (list[int] | None):
                Optional pool of rotations in degrees; sampled per item unless the
                ItemSpec provides `rotationDeg`. Omit/None to use plugin defaults.

            trial_duration (int | None):
                Hard timeout in ms. If None and `end_when_found=True`, the trial ends
                when all targets are collected. Default None.
            end_when_found (bool):
                If True, automatically end the trial once all targets are found.
                Default True.
            response_ends_trial (bool):
                If True, any user interaction that counts as a response ends the trial,
                even if not all targets are collected. Default False.

            seed (int | None):
                Seed for deterministic placement/sampling. Default None.

            show_star_feedback (bool):
                If True, briefly show a star animation on successful target clicks.
                Default False.
            star_color (str):
                Star feedback color. Default "#f6b500".

            triggers (dict | None):
                Optional event→action mapping, e.g.,
                {"on_all_targets_collected": "end_trial"}.
                Default: {"on_all_targets_collected": "end_trial"}.

            duration (int | None):
                SweetBean convenience alias mirrored to `trial_duration` during build
                (consistent with RSVP). If provided, `trial_duration` is set to this
                value. Default None.
            side_effects (dict | None):
                Optional side-effect configuration passed through to the runtime.

        Emits (added to jsPsych data):
            - clicks (list[dict]): Raw click events ({kind, index, id?, t}).
            - n_targets (int): Number of target items in the trial.
            - n_collected (int): Number of targets collected.
            - tps (list[number]): Timestamps for target pickups.
            - bean_clicks (list[dict]): Mirror of `clicks`.
            - bean_n_targets (int): Mirror of `n_targets`.
            - bean_n_found (int): Mirror of `n_collected`.
            - bean_tps (list[number]): Mirror of `tps`.
            - bean_all_found (bool): Convenience flag (n_collected >= n_targets).

        Notes:
            - Provide item-level `pos` to bypass global placement for specific items.
            - If both `duration` and `trial_duration` are given, `duration` takes
              precedence by being copied into `trial_duration`.
            - Null/None optionals are dropped so the plugin falls back to its defaults.

        Example:
            from sweetbean import Block, Experiment
            from sweetbean.variable import TimelineVariable

            timeline = [
                {
                    "targets": [
                        {"text": "T", "color": "#66ff66"},
                        {"shape": "circle", "color": "#66ff66"},
                    ],
                    "distractors": [
                        {"text": "L", "color": "#ff6666"},
                        {"shape": "square", "color": "#ff6666"},
                        {"shape": "triangle", "color": "#ff6666"},
                    ],
                }
            ]

            stim = Foraging(
                targets=TimelineVariable("targets"),
                distractors=TimelineVariable("distractors"),
                position_mode="grid",
                grid_cols=6, grid_rows=4,
                arena_size_vmin=90, min_gap_vmin=2.5,
                background="#000000", color="#ffffff",
                token_box_size="10vmin", token_font_size="8vmin",
                end_when_found=True, response_ends_trial=False,
                show_star_feedback=True, star_color="#f6b500",
            )

            block = Block([stim], timeline=timeline)
            Experiment([block]).to_html("foraging.html")
        """

        if targets is None:
            targets = []
        if distractors is None:
            distractors = []
        if triggers is None:
            triggers = {"on_all_targets_collected": "end_trial"}

        super().__init__(locals(), side_effects)

    # ---- SweetBean hooks ----

    def _add_special_param(self):
        # Use SweetBean `duration` as jsPsych `trial_duration` (consistent with RSVP).
        if self.arg_js.get("duration") not in (None, "null"):
            self.arg_js["trial_duration"] = self.arg_js["duration"]

        # If user didn’t specify pools, omit them; plugin will fall back to its defaults.
        if not self.arg_js.get("overlay_pool"):
            self.arg_js.pop("overlay_pool", None)
        if not self.arg_js.get("rotation_pool"):
            self.arg_js.pop("rotation_pool", None)

        # Keep `type` as string so SweetBean emits declarative config
        self.arg_js["type"] = self.type

    def _process_response(self):
        # Convenience mirrors (prefixed with bean_)
        # clicks is already an array of {kind,index,id?,t}
        self.js_data += 'data["bean_clicks"] = data["clicks"];'
        self.js_data += 'data["bean_n_targets"] = data["n_targets"];'
        self.js_data += 'data["bean_n_found"] = data["n_collected"];'
        self.js_data += 'data["bean_tps"] = data["tps"];'
        # quick all-found boolean
        self.js_data += (
            'data["bean_all_found"] = (data["n_collected"] >= data["n_targets"]);'
        )

    def _set_before(self):
        # No extra on_load code required; SweetBean preamble already sets document bg.
        pass

    # Language mode not supported (same as RSVP)
    def process_l(self, prompts, get_input, multi_turn, datum=None):
        raise NotImplementedError
