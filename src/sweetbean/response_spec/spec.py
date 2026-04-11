"""Pydantic response specifications for SweetBean v2-style trial specs."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_PROMPT_SILENT = {"prompt_silent": True}


class _SpecBaseModel(BaseModel):
    """Strict base model used by SweetBean spec contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class KeyboardPressResponseSpec(_SpecBaseModel):
    """Keyboard response definition."""

    kind: Literal["keyboard_press"] = "keyboard_press"
    allowed_keys: tuple[str, ...] = Field(
        default_factory=tuple,
        description=(
            "Allowed keyboard keys. When empty, any keypress is accepted "
            "(equivalent to jsPsych ALL_KEYS)."
        ),
    )
    correct_keys: tuple[str, ...] | None = Field(
        default=None,
        description=(
            "Optional key(s) considered correct for feedback/scoring. "
            "When omitted, correctness is not evaluated for this response."
        ),
    )
    max_responses: int | None = Field(
        default=1,
        description=(
            "Maximum number of responses to capture. Default 1. "
            "Use null for no limit (as many responses as occur before the trial ends)."
        ),
    )
    response_ends_trial: bool = Field(
        default=True,
        description="Whether a valid response ends the trial.",
        json_schema_extra=_PROMPT_SILENT,
    )

    @field_validator("max_responses")
    @classmethod
    def _keyboard_max_responses(cls, v: int | None) -> int | None:
        if v is None:
            return None
        if v < 1:
            raise ValueError("max_responses must be >= 1 or null")
        return v


class MouseClickResponseSpec(_SpecBaseModel):
    """Mouse click response definition."""

    kind: Literal["mouse_click"] = "mouse_click"
    target_ids: tuple[str, ...] = Field(
        default_factory=tuple,
        description=(
            "Clickable stimulus ids. When empty, the full scene is clickable: "
            "every rendered stimulus layer counts as a target (full-screen hit "
            "testing over stacked regions)."
        ),
    )
    correct_target_ids: tuple[str, ...] | None = Field(
        default=None,
        description=(
            "Optional target ids considered correct for feedback/scoring. "
            "When omitted, correctness is not evaluated for this response."
        ),
    )
    record_click_x: bool = Field(
        default=True,
        description=(
            "Whether to record click X (viewport/client) in trial data when the "
            "runtime supports it. Default: true."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    record_click_y: bool = Field(
        default=True,
        description=(
            "Whether to record click Y (viewport/client) in trial data when the "
            "runtime supports it. Default: true."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    max_responses: int | None = Field(
        default=1,
        description=(
            "Maximum number of responses to capture. Default 1. "
            "Use null for no limit (as many responses as occur before the trial ends)."
        ),
    )
    response_ends_trial: bool = Field(
        default=True,
        description="Whether a valid response ends the trial.",
        json_schema_extra=_PROMPT_SILENT,
    )

    @field_validator("max_responses")
    @classmethod
    def _mouse_max_responses(cls, v: int | None) -> int | None:
        if v is None:
            return None
        if v < 1:
            raise ValueError("max_responses must be >= 1 or null")
        return v


class SliderResponseSpec(_SpecBaseModel):
    """General scalar rating response using an HTML slider."""

    kind: Literal["slider"] = "slider"
    min_value: float = Field(default=0.0, description="Minimum slider value.")
    max_value: float = Field(default=100.0, description="Maximum slider value.")
    start_value: float | None = Field(
        default=None,
        description=(
            "Optional initial slider value. If omitted, uses midpoint "
            "between min_value and max_value."
        ),
    )
    step: float | None = Field(
        default=None,
        description=(
            "Optional step size. Null means continuous slider; positive values "
            "produce discrete ticks."
        ),
    )
    tick_labels: tuple[str, ...] = Field(
        default_factory=tuple,
        description=(
            "Optional labels shown along the slider (e.g. low/high anchors)."
        ),
    )
    button_label: str = Field(
        default="Continue",
        description="Button label used to submit the rating.",
        json_schema_extra=_PROMPT_SILENT,
    )
    require_movement: bool = Field(
        default=False,
        description=(
            "If true, user must move the slider before submitting."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    correct_values: tuple[float, ...] | None = Field(
        default=None,
        description=(
            "Optional exact value(s) considered correct for feedback/scoring."
        ),
    )
    correct_min_value: float | None = Field(
        default=None,
        description=(
            "Optional lower bound of a correct range (inclusive)."
        ),
    )
    correct_max_value: float | None = Field(
        default=None,
        description=(
            "Optional upper bound of a correct range (inclusive)."
        ),
    )
    max_responses: int | None = Field(
        default=1,
        description=(
            "Maximum number of responses to capture. Default 1. "
            "Use null for no limit (as many responses as occur before the trial ends)."
        ),
    )
    response_ends_trial: bool = Field(
        default=True,
        description="Whether a submitted response ends the trial.",
        json_schema_extra=_PROMPT_SILENT,
    )

    @field_validator("max_responses")
    @classmethod
    def _slider_max_responses(cls, v: int | None) -> int | None:
        if v is None:
            return None
        if v < 1:
            raise ValueError("max_responses must be >= 1 or null")
        return v

    @model_validator(mode="after")
    def _slider_bounds(self) -> "SliderResponseSpec":
        if self.max_value <= self.min_value:
            raise ValueError("max_value must be greater than min_value")
        if self.step is not None and self.step <= 0:
            raise ValueError("step must be > 0 when provided")
        if self.start_value is not None:
            if not (self.min_value <= self.start_value <= self.max_value):
                raise ValueError("start_value must be within [min_value, max_value]")
        if (self.correct_min_value is None) ^ (self.correct_max_value is None):
            raise ValueError(
                "correct_min_value and correct_max_value must be both set or both null"
            )
        if (
            self.correct_min_value is not None
            and self.correct_max_value is not None
            and self.correct_max_value < self.correct_min_value
        ):
            raise ValueError("correct_max_value must be >= correct_min_value")
        return self


ResponseSpecUnion = Annotated[
    KeyboardPressResponseSpec | MouseClickResponseSpec | SliderResponseSpec,
    Field(discriminator="kind"),
]
