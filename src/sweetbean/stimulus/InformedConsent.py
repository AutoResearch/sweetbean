from __future__ import annotations

from html import escape
from typing import Any

from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse


def _sn(d: dict[str, Any], key: str) -> str | None:
    if key not in d:
        return None
    v = d[key]
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


class InformedConsent(HtmlKeyboardResponse):
    """
    SweetBean-compatible informed-consent page.
    Participants continue with space.
    """

    def __init__(self, text: str, duration=None, side_effects=None):
        super().__init__(
            duration=duration,
            stimulus=text,
            choices=[" "],
            correct_key="",
            side_effects=side_effects,
        )

    @classmethod
    def from_sections(
        cls,
        *,
        research_config: dict[str, Any],
        consent_config: dict[str, Any],
    ) -> "InformedConsent":
        title = _sn(research_config, "study_title") or _sn(consent_config, "title")
        text = cls._build_html(
            institution=_sn(research_config, "institution"),
            title=title,
            version=_sn(consent_config, "version"),
            researcher_name=_sn(research_config, "researcher_name"),
            researcher_email=_sn(research_config, "researcher_email"),
            researcher_phone=_sn(research_config, "researcher_phone"),
            duration_minutes=_sn(consent_config, "duration_minutes"),
            compensation_amount=_sn(consent_config, "compensation_amount"),
            age_range=_sn(consent_config, "age_range"),
            compensation_rate=_sn(consent_config, "compensation_rate"),
            purpose=_sn(consent_config, "purpose"),
            procedures=_sn(consent_config, "procedures"),
            risks=_sn(consent_config, "risks"),
            benefits=_sn(consent_config, "benefits"),
            confidentiality=_sn(consent_config, "confidentiality"),
            continue_text=_sn(consent_config, "continue_text"),
        )
        return cls(text=text)

    @staticmethod
    def _build_html(
        *,
        institution: str | None,
        title: str | None,
        version: str | None,
        researcher_name: str | None,
        researcher_email: str | None,
        researcher_phone: str | None,
        duration_minutes: str | None,
        compensation_amount: str | None,
        age_range: str | None,
        compensation_rate: str | None,
        purpose: str | None,
        procedures: str | None,
        risks: str | None,
        benefits: str | None,
        confidentiality: str | None,
        continue_text: str | None,
    ) -> str:
        parts: list[str] = [
            "<div style='max-width:960px;margin:0 auto;padding:24px 28px;text-align:left;"
            "line-height:1.5;font-family:Arial,sans-serif;'>"
        ]
        if institution:
            parts.append(f"<h1 style='margin-bottom:6px;'>{escape(institution)}</h1>")
        parts.append("<h2 style='margin-top:0;'>CONSENT FOR RESEARCH PARTICIPATION</h2>")
        if title:
            parts.append(f"<h3 style='font-weight:normal;'>{escape(title)}</h3>")
        if version:
            parts.append(f"<p><strong>{escape(version)}</strong></p>")

        parts.append("<ul style='padding-left:20px;'>")
        parts.append(
            "<li>You are invited to take part in this study. Participation is "
            "<strong>voluntary</strong>.</li>"
        )

        contact_bits = []
        if researcher_name:
            contact_bits.append(escape(researcher_name))
        if researcher_email:
            contact_bits.append(escape(researcher_email))
        if researcher_phone:
            contact_bits.append(escape(researcher_phone))
        if contact_bits:
            parts.append(
                "<li><strong>RESEARCHER:</strong> " + ", ".join(contact_bits) + "</li>"
            )

        if purpose:
            parts.append(f"<li><strong>PURPOSE:</strong> {escape(purpose)}</li>")
        if procedures:
            parts.append(f"<li><strong>PROCEDURES:</strong> {escape(procedures)}</li>")
        if duration_minutes:
            parts.append(
                "<li><strong>TIME INVOLVED:</strong> "
                f"Up to {escape(duration_minutes)} minutes.</li>"
            )

        comp_parts: list[str] = []
        if compensation_rate and compensation_amount:
            comp_parts.append(
                f"{escape(compensation_rate)}. Estimated base payment for this study is "
                f"${escape(compensation_amount)}."
            )
        elif compensation_rate:
            comp_parts.append(escape(compensation_rate))
        elif compensation_amount:
            comp_parts.append(
                "Estimated base payment for this study is "
                f"${escape(compensation_amount)}."
            )
        if comp_parts:
            parts.append(f"<li><strong>COMPENSATION:</strong> {comp_parts[0]}</li>")

        if risks:
            parts.append(f"<li><strong>RISKS:</strong> {escape(risks)}</li>")
        if benefits:
            parts.append(f"<li><strong>BENEFITS:</strong> {escape(benefits)}</li>")
        if confidentiality:
            parts.append(
                f"<li><strong>CONFIDENTIALITY:</strong> {escape(confidentiality)}</li>"
            )

        parts.append(
            "<li><strong>VOLUNTARY:</strong> You may stop at any time without penalty.</li>"
        )

        if age_range:
            parts.append(
                "<li><strong>ELIGIBILITY:</strong> By continuing you confirm your age is in "
                f"the allowed range ({escape(age_range)}).</li>"
            )

        parts.append("</ul>")
        parts.append(
            "<p>CONSENT TO PARTICIPATE: Continuing confirms that you have read and "
            "understood this information and agree to participate.</p>"
        )
        if continue_text:
            parts.append(f"<p><strong>{escape(continue_text)}</strong></p>")
        parts.append("</div>")
        return "".join(parts)
