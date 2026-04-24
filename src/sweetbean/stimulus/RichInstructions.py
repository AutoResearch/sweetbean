"""
Rich, scroll-friendly instruction screens (html-keyboard-response).

SweetBean ships a global ``div { font-size: 36pt }`` in ``main.css``. Long
instruction pages must wrap content in a scoped stylesheet or nested divs
inherit that size. This module provides the same pattern as
:class:`InformedConsent`: a single wrapper (``.sweetbean-rich-instructions``)
with defensive typography and semantic hooks for your *inner* HTML.

Inner HTML conventions (all optional — plain ``<p>`` / ``<h3>`` work too):

* ``<h3 class="sbri-section">…</h3>`` — section heading (larger than body text).
* ``<ul class="sbri-panel-list">…</ul>`` — inset list / meta panel.
* ``<span class="sbri-accent">…</span>`` — subtle highlight (e.g. percentages).
* ``<div class="sbri-example">…</div>`` — boxed preview block.
* ``<div class="sbri-example-prompt">…</div>`` — prompt line inside the example.
* ``<div class="sbri-example-row">…</div>`` — horizontal row (e.g. two cards).
* ``<div class="sbri-example-keys">…</div>`` — key legend under the example.
* ``<p class="sbri-muted">…</p>`` — secondary note text.
* ``<p class="sbri-press">…</p>`` — footer; used by the default footer when
  ``footer_html`` is omitted.

Pass arbitrary HTML fragments as ``inner_html``; they are inserted verbatim
(only the document ``title`` string is escaped).
"""

from __future__ import annotations

import html
from typing import Any

from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse

_BASE_STYLE = """
<style>
  .sweetbean-rich-instructions{
    box-sizing:border-box;
    max-width:var(--sbri-max-width, 780px);
    margin:0 auto;
    padding:24px 32px 28px 32px;
    text-align:left;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,
                'Helvetica Neue',Arial,sans-serif;
    font-size:var(--sbri-body, 13px) !important;
    line-height:1.5 !important;
    color:#f0f0f0;
    background:transparent;
  }
  /* Descendants only — never match the wrapper with `, .sweetbean-rich-instructions`
     or the wrapper's own font-size would resolve to inherit and pick up 36pt. */
  .sweetbean-rich-instructions *{
    font-size:inherit !important;
    line-height:inherit !important;
  }
  .sweetbean-rich-instructions h2.sbri-title{
    font-size:var(--sbri-title, 32px) !important;
    font-weight:600;
    color:#ffffff;
    text-align:center;
    margin:0 0 18px 0;
    letter-spacing:-0.005em;
  }
  .sweetbean-rich-instructions h3,
  .sweetbean-rich-instructions .sbri-section{
    font-size:var(--sbri-section, 20px) !important;
    font-weight:600;
    color:#ffffff;
    margin:20px 0 6px 0;
    letter-spacing:0.01em;
  }
  .sweetbean-rich-instructions p{margin:0 0 10px 0;}
  .sweetbean-rich-instructions p.sbri-muted{
    font-size:14px !important;
    color:#cfcfcf;
  }
  .sweetbean-rich-instructions strong{color:#ffffff;}
  .sweetbean-rich-instructions ul.sbri-panel-list{
    list-style:none;
    margin:6px 0 0 0;
    padding:10px 14px;
    background:rgba(255,255,255,0.05);
    border-left:3px solid #6a90c0;
    border-radius:4px;
  }
  .sweetbean-rich-instructions ul.sbri-panel-list li{
    display:flex;
    justify-content:space-between;
    margin:0 0 4px 0;
  }
  .sweetbean-rich-instructions ul.sbri-panel-list li:last-child{margin-bottom:0;}
  .sweetbean-rich-instructions .sbri-accent{
    color:#a8c8ff;
    font-variant-numeric:tabular-nums;
  }
  .sweetbean-rich-instructions kbd{
    display:inline-block;
    padding:1px 6px;
    border:1px solid #888;
    border-bottom-width:2px;
    border-radius:4px;
    font-family:Menlo,Consolas,monospace;
    font-size:12px !important;
    background:rgba(255,255,255,0.06);
    color:#ffffff;
  }
  .sweetbean-rich-instructions .sbri-example{
    margin:14px 0 6px 0;
    padding:14px 16px;
    background:rgba(255,255,255,0.04);
    border:1px solid #444;
    border-radius:6px;
    text-align:center;
  }
  .sweetbean-rich-instructions .sbri-example-prompt{
    font-weight:600;
    color:#ffffff;
    margin-bottom:10px;
    font-size:14px !important;
  }
  .sweetbean-rich-instructions .sbri-example-row{
    display:flex;
    justify-content:center;
    gap:8px;
    flex-wrap:wrap;
  }
  .sweetbean-rich-instructions .sbri-example-keys{
    margin-top:10px;
    color:#cfcfcf;
    font-size:12px !important;
  }
  .sweetbean-rich-instructions .sbri-press{
    margin-top:24px;
    padding-top:14px;
    border-top:1px solid #444;
    text-align:center;
    color:#cfcfcf;
    font-size:15px !important;
  }
  .sweetbean-rich-instructions .sbri-press strong{color:#ffffff;}
</style>
""".strip()


def render_rich_instructions_html(
    *,
    title: str = "Instructions",
    inner_html: str,
    footer_html: str | None = None,
    max_width_px: int = 780,
    body_font_px: int = 13,
    title_font_px: int = 32,
    section_font_px: int = 20,
) -> str:
    """Return a full ``<style>`` + wrapper HTML string (for reuse outside the stimulus)."""
    foot = (
        footer_html
        if footer_html is not None
        else "<p class='sbri-press'><strong>Press SPACE to continue.</strong></p>"
    )
    safe_title = html.escape(str(title).strip() or "Instructions", quote=True)
    vars_inline = (
        f"--sbri-max-width:{int(max_width_px)}px;"
        f"--sbri-body:{int(body_font_px)}px;"
        f"--sbri-title:{int(title_font_px)}px;"
        f"--sbri-section:{int(section_font_px)}px;"
    )
    return (
        _BASE_STYLE
        + f"<div class='sweetbean-rich-instructions' style='{vars_inline}'>"
        + f"<h2 class='sbri-title'>{safe_title}</h2>"
        + inner_html
        + foot
        + "</div>"
    )


class RichInstructions(HtmlKeyboardResponse):
    """
    Instruction page with readable typography on SweetBean's dark full-screen UI.

    Participants press SPACE (by default) to continue. Auto-fit is **off** by
    default so long text scrolls naturally.
    """

    fit_to_viewport = False

    def __init__(
        self,
        *,
        title: str = "Instructions",
        inner_html: str,
        footer_html: str | None = None,
        duration: Any = None,
        choices: list[str] | None = None,
        correct_key: str = "",
        side_effects: Any = None,
        fit_to_viewport: bool | None = None,
        max_width_px: int = 780,
        body_font_px: int = 13,
        title_font_px: int = 32,
        section_font_px: int = 20,
    ):
        if choices is None:
            choices = [" "]
        stimulus_html = render_rich_instructions_html(
            title=title,
            inner_html=inner_html,
            footer_html=footer_html,
            max_width_px=max_width_px,
            body_font_px=body_font_px,
            title_font_px=title_font_px,
            section_font_px=section_font_px,
        )
        super().__init__(
            duration=duration,
            stimulus=stimulus_html,
            choices=choices,
            correct_key=correct_key,
            side_effects=side_effects,
            fit_to_viewport=fit_to_viewport,
        )
