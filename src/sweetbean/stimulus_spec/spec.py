"""Pydantic stimulus specifications for layered SweetBean trial rendering."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sweetbean.response_spec.spec import ResponseSpecUnion

_PROMPT_SILENT = {"prompt_silent": True}


class _SpecBaseModel(BaseModel):
    """Strict base model used by SweetBean spec contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class RectangleSpec(_SpecBaseModel):
    """Normalized rectangular placement in viewport coordinates."""

    x: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Horizontal center position in normalized viewport coordinates.",
    )
    y: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Vertical center position in normalized viewport coordinates.",
    )
    width: float = Field(
        default=1.0,
        gt=0.0,
        le=1.0,
        description="Normalized width relative to viewport width.",
    )
    height: float = Field(
        default=1.0,
        gt=0.0,
        le=1.0,
        description="Normalized height relative to viewport height.",
    )


class _BaseStimulusSpec(_SpecBaseModel):
    """Common fields for all stimulus specs."""

    id: str | None = Field(
        default=None,
        description="Optional stable stimulus identifier used for click targeting.",
        json_schema_extra=_PROMPT_SILENT,
    )
    duration_ms: int | None = Field(
        default=None,
        ge=1,
        description="Optional stimulus visibility duration in milliseconds.",
        json_schema_extra=_PROMPT_SILENT,
    )
    z_index: int | None = Field(
        default=None,
        description=(
            "Optional layer order. Higher values render on top. "
            "If omitted, defaults to list order (first stimulus = 0, second = 1, …)."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    rect: RectangleSpec | None = Field(
        default=None,
        description=(
            "Optional placement and size. If omitted, defaults to full viewport "
            "(centered rectangle covering the full screen)."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    opacity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Optional CSS opacity. If omitted, defaults to 1.0 (100% opaque)."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )


class TextStimulusSpec(_BaseStimulusSpec):
    """Rendered text stimulus."""

    kind: Literal["text"] = "text"
    text: str = Field(description="Text content to render.")
    color: str = Field(
        default="white",
        description="CSS text color. Default: white.",
        json_schema_extra=_PROMPT_SILENT,
    )
    font_size_px: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Optional font size in pixels. If omitted, defaults to 32."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    font_family: str | None = Field(
        default=None,
        description=(
            "Optional CSS font-family. If omitted, defaults to sans-serif."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    align: Literal["left", "center", "right"] | None = Field(
        default=None,
        description=(
            "Optional text alignment inside the placement rectangle. "
            "If omitted, defaults to center."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )


class SymbolStimulusSpec(_BaseStimulusSpec):
    """Rendered geometric symbol stimulus."""

    kind: Literal["symbol"] = "symbol"
    shape: Literal["circle", "ring", "rectangle", "triangle", "cross"] = Field(
        description="Symbol geometry to render.",
    )
    color: str = Field(
        default="#111111",
        description="Primary CSS color used for symbol fill/stroke.",
        json_schema_extra=_PROMPT_SILENT,
    )
    size_px: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Optional symbol size in pixels. If omitted, defaults to 160."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    stroke_color: str | None = Field(
        default=None,
        description=(
            "Optional outline color for symbol variants that support stroke."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    stroke_width_px: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Optional outline width in pixels. If omitted, renderer picks a "
            "shape-specific default when needed."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )
    rotation_deg: float | None = Field(
        default=None,
        description=(
            "Optional clockwise symbol rotation in degrees. If omitted, defaults to 0."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )


class AssetStimulusSpec(_BaseStimulusSpec):
    """Rendered visual asset stimulus (image/gif/other browser image asset)."""

    kind: Literal["asset"] = "asset"
    asset_ref: str = Field(
        description=(
            "Asset URL/path, or a timeline placeholder like `{{asset_path_col}}` "
            "resolved from the current CSV row."
        )
    )
    object_fit: Literal["contain", "cover", "fill", "none", "scale-down"] | None = Field(
        default=None,
        description=(
            "Optional CSS object-fit. If omitted, defaults to contain."
        ),
        json_schema_extra=_PROMPT_SILENT,
    )


class BanditArmSpec(_SpecBaseModel):
    """One arm rendered in a bandit stimulus."""

    color: str = Field(
        description="CSS color for the arm border/accent.",
    )
    label: str | None = Field(
        default=None,
        description="Optional arm label shown under the bandit tile.",
    )
    value_text: str | None = Field(
        default=None,
        description="Optional value text shown inside the tile.",
    )


class BanditStimulusSpec(_BaseStimulusSpec):
    """Rendered static multi-armed bandit display."""

    kind: Literal["bandit"] = "bandit"
    bandits: tuple[BanditArmSpec, ...] = Field(
        default_factory=tuple,
        min_length=1,
        description="Bandit arms shown as clickable-style tiles in a grid.",
    )
    title: str | None = Field(
        default=None,
        description="Optional heading text shown above the bandit grid.",
    )
    grid_columns: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Optional explicit number of columns in the grid. "
            "If omitted, renderer picks a near-square layout."
        ),
    )


StimulusSpecUnion = Annotated[
    TextStimulusSpec | SymbolStimulusSpec | AssetStimulusSpec | BanditStimulusSpec,
    Field(discriminator="kind"),
]


class TrialSpec(_SpecBaseModel):
    """One rendered trial containing layered stimuli and response handlers."""

    stimuli: tuple[StimulusSpecUnion, ...] = Field(
        default_factory=tuple,
        min_length=1,
        description="Layered visual stimuli rendered in one trial frame.",
    )
    responses: tuple[ResponseSpecUnion, ...] = Field(
        default_factory=tuple,
        description="Response handlers active for this trial frame.",
    )
    trial_duration_ms: int | None = Field(
        default=None,
        ge=1,
        description="Optional hard cap for total trial duration.",
        json_schema_extra=_PROMPT_SILENT,
    )
    background_color: str = Field(
        default="black",
        description="CSS background color for the trial frame. Default: black.",
        json_schema_extra=_PROMPT_SILENT,
    )

    @model_validator(mode="after")
    def _validate_unique_ids_and_stimulus_defaults(self) -> "TrialSpec":
        ids = [s.id for s in self.stimuli if s.id]
        if len(ids) != len(set(ids)):
            raise ValueError("Stimulus ids must be unique when provided.")

        resolved: list[StimulusSpecUnion] = []
        for i, s in enumerate(self.stimuli):
            updates: dict[str, object] = {}
            if s.z_index is None:
                updates["z_index"] = i
            if s.rect is None:
                updates["rect"] = RectangleSpec()
            if s.opacity is None:
                updates["opacity"] = 1.0
            if isinstance(s, TextStimulusSpec):
                if s.font_size_px is None:
                    updates["font_size_px"] = 32
                if s.font_family is None:
                    updates["font_family"] = "sans-serif"
                if s.align is None:
                    updates["align"] = "center"
            if isinstance(s, SymbolStimulusSpec):
                if s.size_px is None:
                    updates["size_px"] = 160
                if s.rotation_deg is None:
                    updates["rotation_deg"] = 0.0
            if isinstance(s, AssetStimulusSpec):
                if s.object_fit is None:
                    updates["object_fit"] = "contain"
            if updates:
                s = s.model_copy(update=updates)
            resolved.append(s)

        return self.model_copy(update={"stimuli": tuple(resolved)})

