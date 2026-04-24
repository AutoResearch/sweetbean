"""
Informed consent screen: full text as HTML, advance with SPACE (html-keyboard-response).

Two visual styles are supported:

* ``"default"`` (the default): a generic, minimal consent layout that simply lists
  the merged YAML-style fields under bold headings.
* ``"princeton"`` (opt-in): renders the consent in the layout used by the
  Princeton University Adult Consent Form (see ``IRB.pdf`` in the autopi repo).
  Boilerplate text and IRB contact info default to Princeton's; any field can
  still be overridden from the ``consent_config`` dict.

Styling notes
-------------
Sweetbean's bundled ``main.css`` declares a global ``div { font-size: 36pt;
line-height: 40pt }`` rule on top of a black ``body``. Any nested ``<div>``
inside the rendered consent that does NOT carry its own inline ``font-size``
inherits that 36pt — which makes long-form consent text explode. To avoid
that, both renderers prepend a single scoped ``<style>`` block that pins
``font-size: inherit`` on every descendant of ``.sweetbean-informed-consent``;
the more specific selector beats sweetbean's global ``div`` rule, so the
consent's own typography survives. Visual hierarchy is then expressed
through semantic class names (``.ic-title``, ``.ic-section-title``,
``.ic-banner``, ``.ic-press-space``, ``.ic-meta``, ``.ic-clauses``) instead
of brittle per-element inline styles.
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
# shared scoped stylesheet
# ---------------------------------------------------------------------------


# One stylesheet shared by both `default` and `princeton` renderers. The
# critical rule is `.sweetbean-informed-consent * { font-size: inherit }`,
# which beats sweetbean's global `div { font-size: 36pt }` via specificity
# and stops every nested div from blowing up to 36pt. Everything else is
# pure visual hierarchy: a max-width content column, clear section titles,
# comfortable spacing on a dark page.
_BASE_STYLE = """
<style>
  .sweetbean-informed-consent{
    box-sizing:border-box;
    max-width:760px;
    margin:0 auto;
    padding:28px 36px 32px 36px;
    text-align:left;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,
                'Helvetica Neue',Arial,sans-serif;
    font-size:13px;
    line-height:1.5;
    color:#e8e8e8;
    background:transparent;
  }
  /* Beat sweetbean's global `div { font-size: 36pt }` rule via specificity
     so nested divs/sections inherit the wrapper's 13px instead of exploding.
     IMPORTANT: scope the reset to DESCENDANTS only (no leading
     `.sweetbean-informed-consent,` selector). Including the wrapper itself
     would re-resolve its own `font-size` to `inherit` (equal specificity,
     declared after the wrapper's `font-size:13px` → the inherit wins),
     making the wrapper inherit `body`'s 36pt and turning every paragraph
     into giant text while section headings (20px) ended up smaller than
     the body. Headings re-establish their own font-size below; the
     `.sweetbean-informed-consent *` selector has specificity (0,1,0), and
     our `.ic-title` / `.ic-section-title` rules also have specificity
     (0,1,0) but appear later in the stylesheet, so they win. Same for the
     per-class `.ic-banner`, `.ic-subbanner`, `.ic-press-space`, etc. */
  .sweetbean-informed-consent *{
    font-size:inherit;
    line-height:inherit;
  }
  .sweetbean-informed-consent h1,
  .sweetbean-informed-consent h2,
  .sweetbean-informed-consent h3,
  .sweetbean-informed-consent h4{
    color:#ffffff;
    font-weight:600;
    margin:0;
  }
  .sweetbean-informed-consent p{margin:0 0 8px 0;}
  .sweetbean-informed-consent strong{color:#ffffff;}
  .sweetbean-informed-consent .ic-banner{
    font-size:12px;
    font-style:italic;
    color:#a8a8a8;
    text-align:center;
    border-bottom:1px solid #444;
    padding-bottom:10px;
    margin-bottom:14px;
  }
  .sweetbean-informed-consent .ic-subbanner{
    font-size:11px;
    letter-spacing:0.08em;
    text-align:center;
    color:#a8a8a8;
    text-transform:uppercase;
    margin-bottom:18px;
  }
  .sweetbean-informed-consent .ic-title{
    font-size:32px;
    text-align:center;
    margin:0 0 12px 0;
    letter-spacing:-0.005em;
  }
  .sweetbean-informed-consent .ic-meta{
    margin:0 0 18px 0;
    padding:12px 14px;
    background:rgba(255,255,255,0.04);
    border-left:3px solid #6a90c0;
    border-radius:4px;
    font-size:13px;
  }
  .sweetbean-informed-consent .ic-meta p{margin:0 0 4px 0;}
  .sweetbean-informed-consent .ic-meta p:last-child{margin-bottom:0;}
  .sweetbean-informed-consent section{margin:0 0 16px 0;}
  .sweetbean-informed-consent .ic-section-title{
    font-size:20px;
    margin:18px 0 6px 0;
    letter-spacing:0.01em;
  }
  .sweetbean-informed-consent .ic-clauses{
    margin:6px 0 0 0;
    padding:0 0 0 22px;
    list-style:none;
  }
  .sweetbean-informed-consent .ic-clauses li{margin:0 0 8px 0;}
  .sweetbean-informed-consent .ic-clauses li:last-child{margin-bottom:0;}
  .sweetbean-informed-consent .ic-contact-list{
    margin:6px 0 0 0;
    padding:0;
    list-style:none;
  }
  .sweetbean-informed-consent .ic-contact-list li{
    margin:0 0 12px 0;
  }
  .sweetbean-informed-consent .ic-contact-list li:last-child{margin-bottom:0;}
  .sweetbean-informed-consent .ic-press-space{
    margin-top:26px;
    padding-top:14px;
    border-top:1px solid #444;
    text-align:center;
    font-size:15px;
    color:#cfcfcf;
  }
  .sweetbean-informed-consent .ic-press-space strong{color:#ffffff;}
</style>
""".strip()


# ---------------------------------------------------------------------------
# default (generic) style
# ---------------------------------------------------------------------------


def _render_default_html(merged: dict[str, Any]) -> str:
    """Generic, minimal consent layout (the prior default behavior).

    Lists merged YAML-style fields under bold section headings; uses the
    same scoped stylesheet as the Princeton layout so the global sweetbean
    `div` font-size rule does not break the typography.
    """
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
        _BASE_STYLE,
        "<div class='sweetbean-informed-consent'>",
        "<h2 class='ic-title'>Informed consent</h2>",
    ]
    for key, label, raw in sections:
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        body = _fmt_duration(raw) if key == "duration" else _esc(raw)
        parts.append(
            "<section>"
            f"<h3 class='ic-section-title'>{_esc(label)}</h3>"
            f"<p>{body}</p>"
            "</section>"
        )

    parts.append(
        "<p class='ic-press-space'><strong>Press SPACE to continue.</strong></p>"
        "</div>"
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


def _section(label: str, body_html: str) -> str:
    return (
        "<section>"
        f"<h3 class='ic-section-title'>{_esc(label)}</h3>"
        f"{body_html}"
        "</section>"
    )


def _render_princeton_html(merged: dict[str, Any]) -> str:
    """Render consent text in Princeton ADULT CONSENT FORM style (see IRB.pdf).

    Layout:
      * IRB approval banner (italic, muted)
      * "Adult Consent Form — Princeton University" subtitle (uppercase, muted)
      * Title / PI / Department metadata block (subtle highlighted card)
      * Welcome paragraph
      * Purpose, Study Procedures, Benefits/Risks, Confidentiality, Compensation
        as plain sections
      * Who to contact (PI + IRB) as an unordered contact list
      * Consent acknowledgement clauses A / B and final agreement
      * "Press SPACE to continue." footer

    The previous version intermixed an "ADULT CONSENT FORM / PRINCETON
    UNIVERSITY" footer block in the middle of the document; that is now
    promoted to the subtitle right under the banner so the document reads
    top-to-bottom without an interruption.
    """
    study_title = merged.get("study_title") or ""
    pi_name = merged.get("pi_name") or merged.get("researcher_name") or ""
    pi_email = (
        merged.get("pi_email")
        or merged.get("researcher_email")
        or merged.get("email")
        or ""
    )
    institution = _princeton_field(merged, "institution")
    pi_department = _princeton_field(merged, "pi_department")
    irb_contact_name = _princeton_field(merged, "irb_contact_name")
    irb_phone = _princeton_field(merged, "irb_phone")
    irb_email = _princeton_field(merged, "irb_email")
    welcome_text = (
        merged.get("welcome_text") or _PRINCETON_DEFAULTS["welcome_text"]
    )

    purpose = merged.get("purpose")
    procedures = merged.get("procedures")
    duration = merged.get("duration_minutes")
    risks = merged.get("risks")
    benefits = merged.get("benefits")
    confidentiality = merged.get("confidentiality")
    compensation = merged.get("compensation")

    parts: list[str] = [
        _BASE_STYLE,
        "<div class='sweetbean-informed-consent "
        "sweetbean-informed-consent--princeton'>",
        f"<div class='ic-banner'>{_esc(_PRINCETON_HEADER)}</div>",
        "<div class='ic-subbanner'>"
        f"Adult Consent Form &mdash; {institution}"
        "</div>",
        # Metadata card: title / PI / department
        "<div class='ic-meta'>",
        f"<p><strong>TITLE OF RESEARCH:</strong> {_esc(study_title)}</p>",
        f"<p><strong>PRINCIPAL INVESTIGATOR:</strong> {_esc(pi_name)}</p>",
        "<p><strong>PRINCIPAL INVESTIGATOR&rsquo;S DEPARTMENT:</strong> "
        f"{pi_department}</p>",
        "</div>",
        f"<p>{_esc(welcome_text)}</p>",
    ]

    if purpose:
        parts.append(
            _section("Purpose of the research", f"<p>{_esc(purpose)}</p>")
        )

    if procedures or duration:
        body = ""
        if procedures:
            body += f"<p>{_esc(procedures)}</p>"
        if duration:
            body += (
                f"<p>The study duration will be approximately "
                f"{_fmt_duration(duration)}.</p>"
            )
        parts.append(_section("Study Procedures", body))

    if benefits or risks:
        body = ""
        if benefits:
            body += f"<p>{_esc(benefits)}</p>"
        if risks:
            body += f"<p>{_esc(risks)}</p>"
        parts.append(_section("Benefits and Risks", body))

    if confidentiality:
        parts.append(
            _section("Confidentiality", f"<p>{_esc(confidentiality)}</p>")
        )

    if compensation:
        parts.append(
            _section("Compensation", f"<p>{_esc(compensation)}</p>")
        )

    # Contact block: PI + IRB as a clean two-item list.
    contact_items: list[str] = []
    if pi_name or pi_email:
        pi_line = _esc(pi_name)
        if pi_email:
            pi_line += (
                f"<br/><a href='mailto:{_esc(pi_email)}' "
                f"style='color:#a8c8ff;text-decoration:none;'>{_esc(pi_email)}</a>"
            )
        contact_items.append(
            "<li><strong>Principal Investigator</strong><br/>"
            f"{pi_line}</li>"
        )
    contact_items.append(
        "<li><strong>Institutional Review Board</strong> "
        "(if you have questions about your rights as a research subject, or "
        "issues you do not feel you can discuss with the investigator)<br/>"
        f"{irb_contact_name}<br/>"
        f"Phone: {irb_phone}<br/>"
        f"Email: <a href='mailto:{irb_email}' "
        f"style='color:#a8c8ff;text-decoration:none;'>{irb_email}</a></li>"
    )
    parts.append(
        _section(
            "Who to contact with questions",
            f"<ul class='ic-contact-list'>{''.join(contact_items)}</ul>",
        )
    )

    # Final agreement clauses — A / B / C as a plain list under one heading
    # so the numbering does not collide with the contact items above.
    parts.append(
        "<section>"
        "<h3 class='ic-section-title'>Acknowledgement &amp; consent</h3>"
        "<p>I understand the information that was presented and that:</p>"
        "<ol class='ic-clauses' style='list-style:upper-alpha;'>"
        "<li>My participation is voluntary, and I may withdraw my consent and "
        "discontinue participation in the project at any time. My refusal to "
        "participate will not result in any penalty.</li>"
        "<li>I do not waive any legal rights or release "
        f"{institution}, its agents, or you from liability for negligence.</li>"
        "</ol>"
        "<p style='margin-top:10px;'>"
        "I hereby give my consent to be the subject of your research."
        "</p>"
        "</section>"
    )

    parts.append(
        "<p class='ic-press-space'>"
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
