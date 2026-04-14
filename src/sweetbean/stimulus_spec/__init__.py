"""Declarative stimulus + trial specs and jsPsych-backed compiler."""

from sweetbean.stimulus_spec.io import (
    build_html_from_files,
    load_spec_library,
    load_timeline_rows,
    trial_specs_from_files,
    write_prompt_schema_markdown,
)
from sweetbean.stimulus_spec.prompt_schema import build_prompt_schema_markdown
from sweetbean.stimulus_spec.render import compile_trial
from sweetbean.stimulus_spec.spec import (
    AssetStimulusSpec,
    RectangleSpec,
    SymbolStimulusSpec,
    StimulusSpecUnion,
    TextStimulusSpec,
    TrialSpec,
)

__all__ = [
    "AssetStimulusSpec",
    "RectangleSpec",
    "SymbolStimulusSpec",
    "StimulusSpecUnion",
    "TextStimulusSpec",
    "TrialSpec",
    "build_html_from_files",
    "build_prompt_schema_markdown",
    "compile_trial",
    "load_spec_library",
    "load_timeline_rows",
    "trial_specs_from_files",
    "write_prompt_schema_markdown",
]

