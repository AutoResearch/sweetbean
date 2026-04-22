"""
Informed consent screen: full text as HTML, advance with SPACE (html-keyboard-response).

Two visual styles are supported:

* ``"default"`` (the default): a generic, minimal consent layout that simply lists
  the merged YAML-style fields under bold headings.
* ``"princeton"`` (opt-in): renders the consent in the layout used by the
  Princeton University Adult Consent Form (see ``IRB.pdf`` in the autopi repo).
  Boilerplate text and IRB contact info default to Princeton's; any field can
  still be overridden from the ``consent_config`` dict.
"""

from __future__ import annotations

import html
from typing import Any

from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse


def _esc(s: Any) -> str:
    if s is None:
        return ""
    return html.escape(str(s).strip(), quote=True)


def _fmt_duration(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, (int, float)):
        return f"{int(raw)} minutes"
    return _esc(raw)


# ---------------------------------------------------------------------------
# default (generic) style
# ---------------------------------------------------------------------------


def _render_default_html(merged: dict[str, Any]) -> str:
    """Generic, minimal consent layout (the prior default behavior)."""
    researcher = merged.get("researcher_name") or merged.get("pi_name")
    email = merged.get("researcher_email") or merged.get("email")

    sections: list[tuple[str, str, Any]] = [
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
        "<div class='sweetbean-informed-consent' "
        "style='max-width:40rem;margin:auto;text-align:left;'>",
        "<h2 style='text-align:center;'>Informed consent</h2>",
    ]
    for key, label, raw in sections:
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        body = _fmt_duration(raw) if key == "duration" else _esc(raw)
        parts.append(
            f"<section style='margin-bottom:1rem;'>"
            f"<h3>{_esc(label)}</h3><p>{body}</p></section>"
        )

    parts.append(
        "<p style='margin-top:1.5rem;text-align:center;'>"
        "<strong>Press SPACE to continue.</strong>"
        "</p></div>"
    )
    return "".join(parts)


# ---------------------------------------------------------------------------
# Princeton style (opt-in)
# ---------------------------------------------------------------------------


_PRINCETON_HEADER = (
    "This study has been approved by the Institutional Review Board for Human Subjects"
)


_PRINCETON_DEFAULTS: dict[str, str] = {
    "institution": "Princeton University",
    "pi_department": "Psychology",
    "irb_contact_name": "Assistant Director, Research Integrity and Assurance",
    "irb_phone": "(609) 258-8543",
    "irb_email": "irb@princeton.edu",
    "welcome_text": (
        "You are being invited to take part in a research study. Before you decide "
        "to participate in this study, it is important that you understand why the "
        "research is being done and what it will involve. Please take the time to "
        "read the following information carefully. Please ask the researcher if "
        "there is anything that is not clear or if you need more information."
    ),
}


def _princeton_field(merged: dict[str, Any], key: str) -> str:
    """Get a Princeton-style field, falling back to Princeton defaults."""
    val = merged.get(key)
    if val is None or (isinstance(val, str) and not val.strip()):
        val = _PRINCETON_DEFAULTS.get(key, "")
    return _esc(val)


def _princeton_banner() -> str:
    return (
        "<div style='font-style:italic;text-align:center;"
        "border-bottom:1px solid #888;padding-bottom:6px;margin-bottom:18px;'>"
        f"{_esc(_PRINCETON_HEADER)}</div>"
    )


def _princeton_section(label: str, body_html: str) -> str:
    return (
        "<section style='margin:0 0 16px 0;'>"
        f"<h3 style='margin:0 0 6px 0;font-size:15px;font-weight:bold;'>"
        f"{_esc(label)}</h3>"
        f"<div style='margin:0;'>{body_html}</div>"
        "</section>"
    )


def _princeton_paragraph(text: Any) -> str:
    return f"<p style='margin:0 0 8px 0;'>{_esc(text)}</p>"


def _render_princeton_html(merged: dict[str, Any]) -> str:
    """Render consent text in Princeton ADULT CONSENT FORM style (see IRB.pdf)."""
    study_title = merged.get("study_title") or ""
    pi_name = merged.get("pi_name") or merged.get("researcher_name") or ""
    pi_email = merged.get("pi_email") or merged.get("researcher_email") or merged.get("email") or ""
    institution = _princeton_field(merged, "institution")
    pi_department = _princeton_field(merged, "pi_department")
    irb_contact_name = _princeton_field(merged, "irb_contact_name")
    irb_phone = _princeton_field(merged, "irb_phone")
    irb_email = _princeton_field(merged, "irb_email")
    welcome_text = merged.get("welcome_text") or _PRINCETON_DEFAULTS["welcome_text"]

    purpose = merged.get("purpose")
    procedures = merged.get("procedures")
    duration = merged.get("duration_minutes")
    risks = merged.get("risks")
    benefits = merged.get("benefits")
    confidentiality = merged.get("confidentiality")
    compensation = merged.get("compensation")

    parts: list[str] = [
        "<div class='sweetbean-informed-consent sweetbean-informed-consent--princeton' "
        "style='max-width:46rem;margin:auto;text-align:left;font-size:14px;"
        "line-height:1.5;color:#222;'>",
        _princeton_banner(),
        # Title block
        "<div style='margin-bottom:18px;'>",
        f"<p style='margin:0;'><strong>TITLE OF RESEARCH:</strong> {_esc(study_title)}</p>",
        f"<p style='margin:0;'><strong>PRINCIPAL INVESTIGATOR:</strong> {_esc(pi_name)}</p>",
        "<p style='margin:0;'><strong>PRINCIPAL INVESTIGATOR&rsquo;S DEPARTMENT:</strong> "
        f"{pi_department}</p>",
        "</div>",
        _princeton_paragraph(welcome_text),
    ]

    if purpose:
        parts.append(_princeton_section("Purpose of the research:", _princeton_paragraph(purpose)))

    if procedures or duration:
        body = ""
        if procedures:
            body += _princeton_paragraph(procedures)
        if duration:
            body += (
                "<p style='margin:0 0 8px 0;'>"
                f"The study duration will be approximately {_fmt_duration(duration)}.</p>"
            )
        parts.append(_princeton_section("Study Procedures:", body))

    # "ADULT CONSENT FORM / PRINCETON UNIVERSITY" footer block (matches the
    # repeated footer between pages of the PDF). We render it once, in-line.
    parts.append(
        "<div style='text-align:center;margin:18px 0;font-weight:bold;letter-spacing:0.04em;'>"
        "ADULT CONSENT FORM<br/>"
        f"{institution.upper()}"
        "</div>"
    )

    if benefits or risks:
        body = ""
        if benefits:
            body += _princeton_paragraph(benefits)
        if risks:
            body += _princeton_paragraph(risks)
        parts.append(_princeton_section("Benefits and Risks:", body))

    if confidentiality:
        parts.append(
            _princeton_section("Confidentiality:", _princeton_paragraph(confidentiality))
        )

    if compensation:
        parts.append(
            _princeton_section("Compensation:", _princeton_paragraph(compensation))
        )

    # "Who to contact" block — always rendered (uses Princeton IRB defaults)
    contact_body_parts: list[str] = []
    if pi_name or pi_email:
        contact_body_parts.append(
            "<p style='margin:0 0 8px 0;'>"
            "<strong>1.&nbsp;&nbsp;PRINCIPAL INVESTIGATOR:</strong><br/>"
            f"{_esc(pi_name)}"
            f"{('<br/>' + _esc(pi_email)) if pi_email else ''}"
            "</p>"
        )
    contact_body_parts.append(
        "<p style='margin:0 0 8px 0;'>"
        "<strong>2.&nbsp;&nbsp;</strong>If you have questions regarding your rights as "
        "a research subject, or if problems arise which you do not feel you can discuss "
        "with the Investigator, please contact the Institutional Review Board at:<br/>"
        f"{irb_contact_name}<br/>"
        f"Phone: {irb_phone}<br/>"
        f"Email: {irb_email}"
        "</p>"
    )
    parts.append(_princeton_section("Who to contact with questions:", "".join(contact_body_parts)))

    # Final agreement clauses
    parts.append(
        "<section style='margin:18px 0 12px 0;'>"
        "<p style='margin:0 0 8px 0;'><strong>3.&nbsp;&nbsp;</strong>"
        "I understand the information that was presented and that:</p>"
        "<p style='margin:0 0 6px 18px;'><strong>A.</strong>&nbsp;&nbsp;My participation "
        "is voluntary, and I may withdraw my consent and discontinue participation in "
        "the project at any time. My refusal to participate will not result in any penalty.</p>"
        "<p style='margin:0 0 8px 18px;'><strong>B.</strong>&nbsp;&nbsp;I do not waive "
        "any legal rights or release "
        f"{institution}, its agents, or you from liability for negligence.</p>"
        "<p style='margin:0;'><strong>4.&nbsp;&nbsp;</strong>"
        "I hereby give my consent to be the subject of your research.</p>"
        "</section>"
    )

    parts.append(
        "<p style='margin-top:1.5rem;text-align:center;'>"
        "<strong>Press SPACE to continue.</strong>"
        "</p></div>"
    )
    return "".join(parts)


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------


_STYLES = {
    "default": _render_default_html,
    "princeton": _render_princeton_html,
}


def _render_consent_html(merged: dict[str, Any], style: str = "default") -> str:
    """
    Build consent HTML from flat YAML-style keys (see autopi ``consent.yaml``).

    ``research_config`` and ``consent_config`` are merged in ``from_sections``;
    older keys like ``pi_name`` / ``duration_minutes`` are supported as aliases.

    The ``style`` argument selects the visual layout. The default is a generic
    minimal layout; pass ``style="princeton"`` to opt in to a Princeton
    University Adult Consent Form layout (see ``IRB.pdf``).
    """
    renderer = _STYLES.get(style)
    if renderer is None:
        valid = ", ".join(sorted(_STYLES))
        raise ValueError(f"Unknown consent style {style!r}; expected one of: {valid}")
    return renderer(merged)


class InformedConsent(HtmlKeyboardResponse):
    """
    Presents merged research/consent fields as HTML; participant presses SPACE to continue.
    No separate ``continue_text`` field — the footer copy is fixed in English.

    Pass ``style="princeton"`` to :meth:`from_sections` to render in the
    Princeton University ADULT CONSENT FORM layout (see ``IRB.pdf``).

    Auto-fit is **disabled** by default for this stimulus: consent text is
    typically too long to scale-to-fit and should remain readable at its
    natural font size with the trial scrolling normally. Override with
    ``fit_to_viewport=True`` per-instance if you really want the consent
    body shrunk to one screen. See AUTHORING.md §"Auto-fit to viewport".
    """

    fit_to_viewport = False

    @classmethod
    def from_sections(
        cls,
        *,
        research_config: dict[str, Any] | None = None,
        consent_config: dict[str, Any] | None = None,
        duration: Any = None,
        side_effects: Any = None,
        style: str = "default",
    ) -> InformedConsent:
        """
        Merge ``research_config`` then ``consent_config`` (consent wins on key clashes),
        render HTML, and return an :class:`HtmlKeyboardResponse` trial with SPACE to advance.

        :param style: Visual layout. ``"default"`` (the default) keeps the original
            generic layout; ``"princeton"`` opts in to the Princeton University
            Adult Consent Form layout described in ``IRB.pdf``.
        """
        a = dict(research_config or {})
        b = dict(consent_config or {})
        merged = {**a, **b}
        stimulus_html = _render_consent_html(merged, style=style)
        return cls(
            duration=duration,
            stimulus=stimulus_html,
            choices=[" "],
            correct_key="",
            side_effects=side_effects,
        )
