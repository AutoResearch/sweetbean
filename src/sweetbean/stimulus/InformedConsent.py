"""
Informed consent screen: full text as HTML, advance with SPACE (html-keyboard-response).
"""

from __future__ import annotations

import html
from typing import Any

from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse


def _esc(s: Any) -> str:
    if s is None:
        return ""
    return html.escape(str(s).strip(), quote=True)


def _render_consent_html(merged: dict[str, Any]) -> str:
    """
    Build consent HTML from flat YAML-style keys (see autopi ``consent.yaml``).
    ``research_config`` and ``consent_config`` are merged in ``from_sections``; older
    keys like ``pi_name`` / ``duration_minutes`` are supported as aliases.
    """
    # Prefer explicit researcher_name; fall back to legacy pi_name
    researcher = merged.get("researcher_name") or merged.get("pi_name")
    email = merged.get("researcher_email") or merged.get("email")

    sections: list[tuple[str, str, str]] = [
        ("institution", "Institution", merged.get("institution")),
        ("researcher", "Researcher", researcher),
        ("contact", "Contact", email),
        ("study_title", "Study title", merged.get("study_title")),
        ("age_range", "Eligible age range", merged.get("age_range")),
        ("duration", "Duration", merged.get("duration_minutes")),
        ("purpose", "Purpose", merged.get("purpose")),
        ("procedures", "Procedures", merged.get("procedures")),
        ("risks", "Risks", merged.get("risks")),
        ("benefits", "Benefits", merged.get("benefits")),
        ("confidentiality", "Confidentiality", merged.get("confidentiality")),
    ]

    parts: list[str] = [
        "<div class='sweetbean-informed-consent' style='max-width:40rem;margin:auto;text-align:left;'>",
        "<h2 style='text-align:center;'>Informed consent</h2>",
    ]
    for _key, label, raw in sections:
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        if _key == "duration" and isinstance(raw, (int, float)):
            body = f"{int(raw)} minutes"
        else:
            body = _esc(raw)
        parts.append(f"<section style='margin-bottom:1rem;'><h3>{_esc(label)}</h3><p>{body}</p></section>")

    parts.append(
        "<p style='margin-top:1.5rem;text-align:center;'>"
        "<strong>Press SPACE to continue.</strong>"
        "</p></div>"
    )
    return "".join(parts)


class InformedConsent(HtmlKeyboardResponse):
    """
    Presents merged research/consent fields as HTML; participant presses SPACE to continue.
    No separate ``continue_text`` field — the footer copy is fixed in English.
    """

    @classmethod
    def from_sections(
        cls,
        *,
        research_config: dict[str, Any] | None = None,
        consent_config: dict[str, Any] | None = None,
        duration: Any = None,
        side_effects: Any = None,
    ) -> InformedConsent:
        """
        Merge ``research_config`` then ``consent_config`` (consent wins on key clashes),
        render HTML, and return a :class:`HtmlKeyboardResponse` trial with SPACE to advance.
        """
        a = dict(research_config or {})
        b = dict(consent_config or {})
        merged = {**a, **b}
        stimulus_html = _render_consent_html(merged)
        return cls(
            duration=duration,
            stimulus=stimulus_html,
            choices=[" "],
            correct_key="",
            side_effects=side_effects,
        )
