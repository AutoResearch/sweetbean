"""Compile declarative trial specs into SweetBean stimuli (jsPsych-backed)."""

from __future__ import annotations

import math
from html import escape
from pathlib import Path

from sweetbean.stimulus.Choice import HtmlChoice
from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse
from sweetbean.stimulus.HtmlSliderResponse import HtmlSliderResponse
from sweetbean.stimulus_spec.spec import (
    AssetStimulusSpec,
    BanditStimulusSpec,
    SymbolStimulusSpec,
    StimulusSpecUnion,
    TextStimulusSpec,
    TrialSpec,
)


class _JsPsychAllKeys:
    """Serializes to ``jsPsych.ALL_KEYS`` in SweetBean's JS emitter."""

    __slots__ = ()

    def to_js(self) -> str:
        return "jsPsych.ALL_KEYS"


_JS_PSYCH_ALL_KEYS = _JsPsychAllKeys()

_VIDEO_SUFFIXES = frozenset(
    {".mp4", ".webm", ".ogg", ".ogv", ".mov", ".m4v", ".avi"}
)


def _asset_is_video(asset_ref: str) -> bool:
    """True when the path/URL should be rendered as a ``<video>`` element."""
    stem = asset_ref.split("?", 1)[0].split("#", 1)[0]
    return Path(stem).suffix.lower() in _VIDEO_SUFFIXES


def _is_slider_trial(spec: TrialSpec) -> bool:
    if not spec.responses:
        return False
    return spec.responses[0].kind == "slider"


def _scene_outer_style(spec: TrialSpec, background: str) -> str:
    """Scene wrapper CSS.

    Slider trials are laid out by CSS in ``HTML_PREAMBLE`` so controls stay visible.
    In that case, scene should simply fill the available stimulus area.
    """
    if _is_slider_trial(spec):
        return (
            f"position:relative;width:100%;max-width:100vw;"
            f"height:100%;max-height:100%;overflow:hidden;background:{escape(background)};"
        )
    return (
        f"position:relative;width:100%;max-width:100vw;"
        f"height:min(100vh,100dvh);max-height:min(100vh,100dvh);overflow:hidden;"
        f"background:{escape(background)};"
    )


def _max_duration_ms(spec: TrialSpec) -> int | None:
    durations = [s.duration_ms for s in spec.stimuli if s.duration_ms is not None]
    if spec.trial_duration_ms is not None:
        durations.append(spec.trial_duration_ms)
    if not durations:
        return None
    return max(durations)


def _stimulus_id(stim: StimulusSpecUnion, index: int) -> str:
    return stim.id or f"stim_{index}"


def _rect_style(stim: StimulusSpecUnion) -> str:
    left = (stim.rect.x - stim.rect.width / 2.0) * 100.0
    top = (stim.rect.y - stim.rect.height / 2.0) * 100.0
    width = stim.rect.width * 100.0
    height = stim.rect.height * 100.0
    return (
        f"position:absolute;left:{left:.6f}%;top:{top:.6f}%;"
        f"width:{width:.6f}%;height:{height:.6f}%;"
        f"z-index:{stim.z_index};opacity:{stim.opacity};"
    )


def _duration_style(stim: StimulusSpecUnion) -> str:
    if stim.duration_ms is None:
        return ""
    return f"animation:sb_v2_hide 1ms linear {stim.duration_ms}ms forwards;"


def _render_text(stim: TextStimulusSpec, stim_id: str) -> str:
    text = escape(stim.text)
    return (
        f"<div data-sb-stim-id='{escape(stim_id)}' "
        f"style='{_rect_style(stim)}{_duration_style(stim)}"
        "display:flex;align-items:center;justify-content:center;"
        f"text-align:{stim.align};color:{escape(stim.color)};"
        f"font-size:{stim.font_size_px}px;font-family:{escape(stim.font_family)};'>"
        f"{text}</div>"
    )


def _render_asset(stim: AssetStimulusSpec, stim_id: str) -> str:
    style = (
        f"{_rect_style(stim)}{_duration_style(stim)}object-fit:{stim.object_fit};"
    )
    if _asset_is_video(stim.asset_ref):
        # Respect declarative fit (default: contain) to avoid forced cropping.
        video_style = f"{style}object-position:center center;"
        # muted + autoplay: required for reliable playback in most browsers.
        return (
            f"<video data-sb-stim-id='{escape(stim_id)}' "
            f"src='{escape(stim.asset_ref)}' "
            f"style='{video_style}' playsinline muted autoplay preload='auto'></video>"
        )
    return (
        f"<img data-sb-stim-id='{escape(stim_id)}' "
        f"src='{escape(stim.asset_ref)}' alt='' style='{style}'/>"
    )


def _render_symbol(stim: SymbolStimulusSpec, stim_id: str) -> str:
    base_style = (
        f"{_rect_style(stim)}{_duration_style(stim)}display:flex;align-items:center;"
        "justify-content:center;"
    )
    size = int(stim.size_px)
    stroke_color = stim.stroke_color or stim.color
    shape_style = (
        f"position:relative;width:{size}px;height:{size}px;"
        f"transform:rotate({float(stim.rotation_deg):.6f}deg);"
    )

    if stim.shape == "circle":
        return (
            f"<div data-sb-stim-id='{escape(stim_id)}' style='{base_style}'>"
            f"<div style='{shape_style}background:{escape(stim.color)};border-radius:50%;'></div>"
            "</div>"
        )
    if stim.shape == "ring":
        stroke_width = (
            int(stim.stroke_width_px)
            if stim.stroke_width_px is not None
            else max(2, round(size * 0.12))
        )
        return (
            f"<div data-sb-stim-id='{escape(stim_id)}' style='{base_style}'>"
            f"<div style='{shape_style}background:transparent;border-radius:50%;"
            f"border:{stroke_width}px solid {escape(stroke_color)};box-sizing:border-box;'></div>"
            "</div>"
        )
    if stim.shape == "rectangle":
        stroke_css = ""
        if stim.stroke_width_px and stim.stroke_width_px > 0:
            stroke_css = (
                f"border:{int(stim.stroke_width_px)}px solid {escape(stroke_color)};"
                "box-sizing:border-box;"
            )
        return (
            f"<div data-sb-stim-id='{escape(stim_id)}' style='{base_style}'>"
            f"<div style='{shape_style}background:{escape(stim.color)};{stroke_css}'></div>"
            "</div>"
        )
    if stim.shape == "triangle":
        stroke_css = ""
        if stim.stroke_width_px and stim.stroke_width_px > 0:
            stroke_css = (
                f"border:{int(stim.stroke_width_px)}px solid {escape(stroke_color)};"
                "box-sizing:border-box;"
            )
        return (
            f"<div data-sb-stim-id='{escape(stim_id)}' style='{base_style}'>"
            f"<div style='{shape_style}background:{escape(stim.color)};"
            "clip-path:polygon(50% 0%, 0% 100%, 100% 100%);"
            f"{stroke_css}'></div>"
            "</div>"
        )
    if stim.shape == "cross":
        arm = max(2, round(size * 0.28))
        if stim.stroke_width_px is not None and stim.stroke_width_px > 0:
            arm = int(stim.stroke_width_px)
        bar_color = escape(stim.color)
        cross_inner = (
            f"<div style='position:absolute;left:50%;top:0;transform:translateX(-50%);"
            f"width:{arm}px;height:{size}px;background:{bar_color};'></div>"
            f"<div style='position:absolute;left:0;top:50%;transform:translateY(-50%);"
            f"width:{size}px;height:{arm}px;background:{bar_color};'></div>"
        )
        return (
            f"<div data-sb-stim-id='{escape(stim_id)}' style='{base_style}'>"
            f"<div style='{shape_style}'>{cross_inner}</div>"
            "</div>"
        )

    raise ValueError(f"Unsupported symbol shape: {stim.shape!r}")


def _render_bandit(stim: BanditStimulusSpec, stim_id: str) -> str:
    n = len(stim.bandits)
    cols = stim.grid_columns or max(1, math.ceil(math.sqrt(n)))
    title_html = ""
    if stim.title:
        title_html = (
            "<div style='grid-column:1 / -1;text-align:center;"
            "font-size:22px;color:#e5e7eb;font-family:sans-serif;'>"
            f"{escape(stim.title)}</div>"
        )

    arms: list[str] = []
    for arm in stim.bandits:
        label_html = ""
        if arm.label:
            label_html = (
                "<div style='font-size:14px;color:#d1d5db;"
                "font-family:sans-serif;margin-top:8px;'>"
                f"{escape(arm.label)}</div>"
            )
        value_html = ""
        if arm.value_text:
            value_html = (
                "<div style='font-size:18px;color:#f9fafb;font-family:sans-serif;"
                "font-weight:600;'>"
                f"{escape(arm.value_text)}</div>"
            )
        arms.append(
            "<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;"
            "padding:10px;'>"
            f"<div style='width:min(11vw,110px);height:min(11vw,110px);border:4px solid {escape(arm.color)};"
            "border-radius:10px;background:rgba(17,24,39,0.55);display:flex;align-items:center;justify-content:center;'>"
            f"{value_html}</div>{label_html}</div>"
        )

    inner = (
        f"<div style='display:grid;grid-template-columns:repeat({cols}, minmax(110px, 1fr));"
        "gap:14px;width:100%;height:100%;align-content:center;justify-items:center;'>"
        f"{title_html}{''.join(arms)}</div>"
    )
    return (
        f"<div data-sb-stim-id='{escape(stim_id)}' "
        f"style='{_rect_style(stim)}{_duration_style(stim)}padding:16px;box-sizing:border-box;'>"
        f"{inner}</div>"
    )


def _render_stimulus(stim: StimulusSpecUnion, index: int) -> tuple[str, str]:
    stim_id = _stimulus_id(stim, index)
    if isinstance(stim, TextStimulusSpec):
        return stim_id, _render_text(stim, stim_id)
    if isinstance(stim, SymbolStimulusSpec):
        return stim_id, _render_symbol(stim, stim_id)
    if isinstance(stim, AssetStimulusSpec):
        return stim_id, _render_asset(stim, stim_id)
    if isinstance(stim, BanditStimulusSpec):
        return stim_id, _render_bandit(stim, stim_id)
    raise TypeError(f"Unsupported stimulus spec: {type(stim)!r}")


def _build_scene_html(spec: TrialSpec) -> tuple[str, list[tuple[str, str]]]:
    rendered = [_render_stimulus(stim, idx) for idx, stim in enumerate(spec.stimuli)]
    body = "".join(html for _, html in rendered)
    html = (
        "<style>"
        "@keyframes sb_v2_hide { to { visibility:hidden; } }"
        "</style>"
        f"<div style='{_scene_outer_style(spec, spec.background_color)}'>"
        f"{body}</div>"
    )
    return html, rendered


def compile_trial(
    spec: TrialSpec,
) -> HtmlKeyboardResponse | HtmlChoice | HtmlSliderResponse:
    """Compile one declarative trial spec into a SweetBean stimulus object."""
    scene_html, rendered = _build_scene_html(spec)
    if not spec.responses:
        return HtmlKeyboardResponse(
            duration=_max_duration_ms(spec),
            stimulus=scene_html,
            choices=[],
            correct_key="",
        )
    if len(spec.responses) != 1:
        raise ValueError(
            "Current renderer supports exactly one response spec per trial."
        )

    response = spec.responses[0]
    if response.kind == "keyboard_press":
        if response.max_responses is not None and response.max_responses > 1:
            raise ValueError(
                "Keyboard response: max_responses > 1 is not supported by the "
                "renderer yet; use 1 or null (unlimited)."
            )
        correct_key = ""
        if response.correct_keys:
            if len(response.correct_keys) > 1:
                raise ValueError(
                    "Keyboard response currently supports at most one `correct_keys` "
                    "entry for built-in correctness tracking."
                )
            correct_key = response.correct_keys[0]
        keys = list(response.allowed_keys)
        choices: list[str] | _JsPsychAllKeys = (
            keys if keys else _JS_PSYCH_ALL_KEYS
        )
        return HtmlKeyboardResponse(
            duration=_max_duration_ms(spec),
            stimulus=scene_html,
            choices=choices,
            correct_key=correct_key,
        )

    if response.kind == "mouse_click":
        if response.max_responses is not None and response.max_responses > 1:
            raise ValueError(
                "Mouse click response: max_responses > 1 is not supported by the "
                "renderer yet; use 1 or null (unlimited)."
            )
        target_set = set(response.target_ids)
        html_array: list[str] = []
        values: list[str] = []
        for stim_id, stim_html in rendered:
            if target_set and stim_id not in target_set:
                continue
            html_array.append(stim_html)
            values.append(stim_id)
        if not html_array:
            raise ValueError(
                "Mouse click response has no clickable targets after filtering."
            )
        return HtmlChoice(
            duration=_max_duration_ms(spec),
            html_array=html_array,
            values=values,
            correct_values=list(response.correct_target_ids or ()),
            time_after_response=0,
        )

    if response.kind == "slider":
        if response.max_responses is not None and response.max_responses > 1:
            raise ValueError(
                "Slider response: max_responses > 1 is not supported by the "
                "renderer yet; use 1 or null (unlimited)."
            )
        start = (
            response.start_value
            if response.start_value is not None
            else (response.min_value + response.max_value) / 2.0
        )
        return HtmlSliderResponse(
            duration=_max_duration_ms(spec),
            stimulus=scene_html,
            min=response.min_value,
            max=response.max_value,
            slider_start=start,
            step=response.step,
            labels=list(response.tick_labels),
            button_label=response.button_label,
            require_movement=response.require_movement,
            response_ends_trial=response.response_ends_trial,
            correct_values=list(response.correct_values or ()),
            correct_min=response.correct_min_value,
            correct_max=response.correct_max_value,
        )

    raise ValueError(f"Unsupported response kind: {response.kind}")

