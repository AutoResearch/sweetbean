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
