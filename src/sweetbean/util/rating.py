"""Build-time HTML helpers for cardinal-rating displays.

These are **Python-time** helpers — they return plain HTML strings to be
embedded into a stimulus's pre-rendered HTML or returned from a
`FunctionVariable` callable that runs at trial render time. They are
intentionally tiny (no runtime JS, no transpilation) so they slot
into either of the patterns described in
``vendor/sweetbean/src/sweetbean/stimulus/AUTHORING.md``:

* **Pattern A** (pre-render in Python): build the row HTML at construct
  time and ship it as a string ``TimelineVariable``.
* **Pattern B** (literals-only ``FunctionVariable``): the helpers are
  pure expressions, so you can copy the body into your own
  ``FunctionVariable`` callable if the row needs to depend on
  per-trial values that aren't known at build time. (Don't import
  these helpers *inside* a ``FunctionVariable`` callable — they're not
  Transcrypt-safe.)

What's here
-----------
``rating_bar_html(value, max_value, ...)``
    Single horizontal bar with optional numeric label. Replaces the
    "row of pips" idiom that breaks down past `max_value=4` or so.
``rating_row_html(label, value, max_value, ...)``
    A two-column row: left = label (e.g. "Expert 1 (75%)"), right =
    rating bar. This is the unit you usually want for "expert ratings"
    style displays.
``rating_card_html(title, rows_html, ...)``
    Thin wrapper that titles a stack of ``rating_row_html`` outputs
    with a card border (e.g. one card per option in a
    forced-choice task).

Why a horizontal bar instead of pips
------------------------------------
Pips work for binary or ~3-level features but become visual clutter
fast (a row of 7 circles is hard to read at a glance). A filled bar
plus a numeric label scales naturally to any ``max_value`` and reads
the same way at ``max_value=1`` (full or empty bar) as at
``max_value=10`` (a 4/10 looks like 40% fill). Same primitive, every
``rating_max``.

All helpers escape user-supplied label / title strings via
``html.escape`` to keep the embedded HTML well-formed.
"""

from __future__ import annotations

import html
from typing import Iterable

__all__ = [
    "rating_bar_html",
    "rating_row_html",
    "rating_card_html",
    "rating_card_from_values_html",
]


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def rating_bar_html(
    value: float,
    max_value: float,
    *,
    width_px: int = 110,
    height_px: int = 14,
    fill_color: str = "#4682B4",
    track_color: str = "rgba(255,255,255,0.08)",
    border_color: str = "#888",
    show_value: bool = True,
    value_units: str = "",
) -> str:
    """Return HTML for a single horizontal rating bar.

    A fixed-width track (``width_px`` × ``height_px``) is filled to
    ``value / max_value``. ``value`` is clamped to ``[0, max_value]``
    so out-of-range values render gracefully instead of overflowing
    the track. When ``show_value`` is True, an aligned numeric label
    (``"<value>/<max_value>"`` plus optional ``value_units``) is
    rendered to the right of the bar.

    All visual params have defaults that match the dark-mode jsPsych
    defaults; override per-call if your stimulus uses a different
    palette.
    """
    max_value = max(1e-9, float(max_value))
    v = _clamp(float(value), 0.0, max_value)
    pct = 100.0 * v / max_value
    fill_html = (
        f"<span style='display:block;height:100%;width:{pct:.4g}%;"
        f"background:{fill_color};border-radius:2px;'></span>"
    )
    track_html = (
        f"<span style='display:inline-block;vertical-align:middle;"
        f"width:{int(width_px)}px;height:{int(height_px)}px;"
        f"background:{track_color};border:1px solid {border_color};"
        f"border-radius:3px;overflow:hidden;'>"
        f"{fill_html}</span>"
    )
    if not show_value:
        return track_html
    pretty_value = f"{v:g}" if isinstance(value, float) else str(int(v))
    pretty_max = f"{max_value:g}" if isinstance(max_value, float) else str(int(max_value))
    units = (" " + html.escape(value_units)) if value_units else ""
    label_html = (
        f"<span style='display:inline-block;vertical-align:middle;"
        f"margin-left:8px;font-variant-numeric:tabular-nums;font-size:13px;'>"
        f"{html.escape(pretty_value)}/{html.escape(pretty_max)}{units}</span>"
    )
    return track_html + label_html


def rating_row_html(
    label: str,
    value: float,
    max_value: float,
    *,
    label_color: str = "#dddddd",
    label_min_width_px: int = 110,
    bar_kwargs: dict | None = None,
) -> str:
    """A two-column row: left label + right rating bar.

    Use one of these per feature/expert; stack them inside a
    ``rating_card_html`` to build a per-option panel. ``label`` is
    HTML-escaped, so pass a plain string like ``"Expert 1 (75%)"``.
    """
    bar = rating_bar_html(value, max_value, **(bar_kwargs or {}))
    return (
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        f"gap:10px;margin:4px 0;font-size:13px;color:{label_color};'>"
        f"<span style='display:inline-block;min-width:{int(label_min_width_px)}px;"
        "white-space:nowrap;'>"
        f"{html.escape(label)}</span>"
        f"<span style='display:inline-flex;align-items:center;'>{bar}</span>"
        "</div>"
    )


def rating_card_html(
    title: str,
    rows_html: str | Iterable[str],
    *,
    title_color: str = "#ffffff",
    border_color: str = "#888",
    background: str = "transparent",
    min_width_px: int = 240,
) -> str:
    """Bordered card with a title and a stack of rating rows.

    ``rows_html`` may be a single concatenated HTML string or any
    iterable of row strings (which are joined with no separator). The
    card has a fixed minimum width so two adjacent cards line up cleanly
    in a flex row even when their longest labels differ.
    """
    if not isinstance(rows_html, str):
        rows_html = "".join(rows_html)
    return (
        "<div style='display:inline-block;vertical-align:top;"
        f"margin:0 14px;padding:10px 14px;border:2px solid {border_color};"
        f"border-radius:8px;min-width:{int(min_width_px)}px;"
        f"background:{background};text-align:left;'>"
        f"<h3 style='margin:0 0 6px 0;font-size:16px;text-align:center;"
        f"color:{title_color};'>{html.escape(title)}</h3>"
        f"{rows_html}"
        "</div>"
    )


def rating_card_from_values_html(
    title: str,
    labels: Iterable[str],
    values: Iterable[float],
    max_value: float,
    *,
    bar_kwargs: dict | None = None,
    card_kwargs: dict | None = None,
) -> str:
    """Convenience: build a rating card straight from parallel
    ``labels`` and ``values`` iterables.

    Equivalent to::

        rating_card_html(
            title,
            [rating_row_html(lbl, v, max_value, bar_kwargs=bar_kwargs)
             for lbl, v in zip(labels, values)],
            **(card_kwargs or {}),
        )

    but spelled in one line at the call site, which is useful when you
    have one card per option in a forced-choice display.
    """
    rows = "".join(
        rating_row_html(lbl, v, max_value, bar_kwargs=bar_kwargs)
        for lbl, v in zip(labels, values)
    )
    return rating_card_html(title, rows, **(card_kwargs or {}))
