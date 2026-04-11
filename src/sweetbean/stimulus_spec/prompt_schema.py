"""LLM schema helpers for SweetBean declarative trial specs.

This module intentionally has no hard dependency on ``auto-prompt``.
If available, it is used to build richer markdown docs; otherwise a
JSON-schema fallback is returned.
"""

from __future__ import annotations

import json

from pydantic import TypeAdapter

from sweetbean.response_spec.spec import ResponseSpecUnion
from sweetbean.stimulus_spec.spec import StimulusSpecUnion, TrialSpec


def build_prompt_schema_markdown(*, verbosity: int = 1) -> str:
    """Return markdown documentation for SweetBean trial-spec models.

    *verbosity* is passed to ``auto_prompt.build_prompt`` when available;
    higher values include fields marked with ``prompt_verbosity_min``.
    """
    try:
        from auto_prompt import build_prompt  # type: ignore
    except Exception:
        payload = {
            "TrialSpec": TrialSpec.model_json_schema(),
            "StimulusSpecUnion": TypeAdapter(StimulusSpecUnion).json_schema(),
            "ResponseSpecUnion": TypeAdapter(ResponseSpecUnion).json_schema(),
        }
        return "```json\n" + json.dumps(payload, indent=2, default=str) + "\n```"
    interpolation_guide = (
        "# TIMELINE PLACEHOLDER GUIDE\n\n"
        "- Any string field may use `{{column_name}}` placeholders.\n"
        "- Placeholders are resolved from the current timeline CSV row before validation/rendering.\n"
        "- Use literal values (direct strings/numbers) when no per-row substitution is needed.\n"
        "- Example: `asset_ref: \"{{asset_ref}}\"`, `text: \"{{prompt_text}}\"`.\n"
        "\n"
        "# RUNTIME FEEDBACK NOTES\n\n"
        "- Response handlers emit normalized fields in jsPsych data when available:\n"
        "  `bean_response`, `bean_rt`, `bean_correct`, and plugin-specific values like `bean_value`.\n"
        "- These can be consumed by dynamic SweetBean/JS logic in later trials "
        "(e.g. feedback screens based on previous correctness).\n"
    )
    return "\n\n".join(
        [
            interpolation_guide,
            "# SCHEMA - TrialSpec",
            build_prompt(TrialSpec, verbosity=verbosity),
            "# SCHEMA - StimulusSpecUnion",
            build_prompt(StimulusSpecUnion, verbosity=verbosity),
            "# SCHEMA - ResponseSpecUnion",
            build_prompt(ResponseSpecUnion, verbosity=verbosity),
        ]
    )

