"""IO helpers: build declarative SweetBean trials from JSON + CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus_spec.render import compile_trial
from sweetbean.stimulus_spec.spec import TrialSpec
from sweetbean.stimulus_spec.prompt_schema import build_prompt_schema_markdown


def _decode_cell(raw: str) -> Any:
    """Decode timeline cells.

    - Plain strings remain strings.
    - JSON-looking values (`{...}` / `[...]`) are parsed as JSON.
    """
    s = raw.strip()
    if not s:
        return ""
    if (s.startswith("{") and s.endswith("}")) or (
        s.startswith("[") and s.endswith("]")
    ):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s
    return s


def load_spec_library(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load reusable trial-spec templates from JSON file."""
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    raw_specs = payload.get("specs")
    if not isinstance(raw_specs, dict) or not raw_specs:
        raise ValueError("Spec file must contain a non-empty 'specs' object.")
    out: dict[str, dict[str, Any]] = {}
    for spec_id, raw in raw_specs.items():
        if not isinstance(spec_id, str) or not spec_id.strip():
            raise ValueError("All spec ids must be non-empty strings.")
        if not isinstance(raw, dict):
            raise ValueError(f"Spec '{spec_id}' must be a JSON object.")
        out[spec_id] = raw
    return out


def load_timeline_rows(path: str | Path) -> list[dict[str, Any]]:
    """Load timeline rows from CSV.

    Required column: `spec_id`
    """
    p = Path(path)
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "spec_id" not in (reader.fieldnames or []):
            raise ValueError("Timeline CSV must contain a 'spec_id' column.")
        for row_idx, row in enumerate(reader, start=1):
            clean = {k: _decode_cell(v or "") for k, v in row.items() if k}
            sid = str(clean.get("spec_id", "")).strip()
            if not sid:
                raise ValueError(f"Missing spec_id at timeline row {row_idx}.")
            clean["spec_id"] = sid
            rows.append(clean)
    if not rows:
        raise ValueError("Timeline CSV is empty.")
    return rows


def _resolve_templates(value: Any, row: dict[str, Any]) -> Any:
    """Resolve `{{column_name}}` placeholders from one timeline row."""
    if isinstance(value, dict):
        return {k: _resolve_templates(v, row) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_templates(v, row) for v in value]
    if isinstance(value, str):
        if value.startswith("{{") and value.endswith("}}"):
            key = value[2:-2].strip()
            return row.get(key, "")
        return value
    return value


def trial_specs_from_files(
    spec_json_path: str | Path,
    timeline_csv_path: str | Path,
) -> list[TrialSpec]:
    """Materialize validated TrialSpec list from JSON templates + timeline CSV."""
    specs = load_spec_library(spec_json_path)
    timeline = load_timeline_rows(timeline_csv_path)

    out: list[TrialSpec] = []
    for row in timeline:
        sid = row["spec_id"]
        if sid not in specs:
            raise KeyError(f"Timeline references unknown spec_id '{sid}'.")
        resolved = _resolve_templates(specs[sid], row)
        out.append(TrialSpec.model_validate(resolved))
    return out


def build_html_from_files(
    spec_json_path: str | Path,
    timeline_csv_path: str | Path,
    out_html_path: str | Path,
) -> Path:
    """Compile and write a runnable jsPsych HTML from declarative files."""
    trials = trial_specs_from_files(spec_json_path, timeline_csv_path)
    compiled = [compile_trial(t) for t in trials]
    exp = Experiment([Block(compiled)])
    out = Path(out_html_path)
    exp.to_html(str(out))
    return out


def write_prompt_schema_markdown(
    out_path: str | Path, *, verbosity: int = 1
) -> Path:
    """Generate and write markdown docs for Trial/Stimulus/Response specs."""
    out = Path(out_path)
    out.write_text(
        build_prompt_schema_markdown(verbosity=verbosity) + "\n",
        encoding="utf-8",
    )
    return out

