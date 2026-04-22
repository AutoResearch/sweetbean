"""Discrete N-point rating widget that doubles as a static display.

Two modes, switched by the `value` argument:

- **Display mode** (`value` is an int 0..n_points): renders the rating with
  the first `value` pips filled. No input is collected; the trial
  auto-advances after `duration` ms (default 1500 ms when not specified).
- **Response mode** (`value is None`): renders an empty rating; the subject
  presses a number key `1`..`n_points` to choose a value. The pressed key
  is recorded as `bean_response` (string of the digit). The trial ends on
  any valid key press.

Use the module-level :func:`render_rating_html` helper to embed a rating
bar inside the HTML string of another stimulus (e.g. when several ratings
appear together as part of a larger choice screen).
"""

from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse
from sweetbean.variable import FunctionVariable, Variable


_FILLED_COLOR = "#4682B4"
_EMPTY_BORDER = "#888"
_PIP_PX = 22
_PIP_GAP_PX = 8


def _validate_n_points(n_points):
    # 1..10. n_points=1 is the binary on/off indicator (single pip).
    if not isinstance(n_points, int) or n_points < 1 or n_points > 10:
        raise ValueError(
            f"n_points must be an integer in 1..10, got {n_points!r}."
        )


def _validate_value(value, n_points):
    if value is None:
        return
    if not isinstance(value, int) or value < 0 or value > n_points:
        raise ValueError(
            f"value must be an integer in 0..{n_points}, got {value!r}."
        )


def render_rating_html(value, n_points, label=None):
    """Return an HTML snippet for an N-point rating bar.

    Arguments:
        value (int | None): If int, the first `value` pips are filled.
            If None, all pips are empty (response-mode appearance).
        n_points (int): Total number of pips, 1..10. (n_points=1 gives a
            single pip that is either filled or empty — a binary
            on/off indicator.)
        label (str | None): Optional caption rendered above the pips.

    Returns:
        str: HTML suitable for embedding in another stimulus's `stimulus`
        argument or in a larger HTML composition.

    Notes:
        - Pure literals only — safe to call from inside a sweetbean
          FunctionVariable (Transcrypt rejects non-local globals).
        - Renders inline-block; layout flows with surrounding HTML.
    """
    _validate_n_points(n_points)
    _validate_value(value, n_points)
    fill = 0 if value is None else int(value)

    pips = []
    for i in range(n_points):
        is_filled = i < fill
        bg = _FILLED_COLOR if is_filled else "transparent"
        border = "none" if is_filled else f"2px solid {_EMPTY_BORDER}"
        pips.append(
            f"<div style='display:inline-block;width:{_PIP_PX}px;"
            f"height:{_PIP_PX}px;border-radius:50%;background:{bg};"
            f"border:{border};margin-right:{_PIP_GAP_PX}px;'></div>"
        )
    pip_row = (
        f"<div style='display:inline-block;line-height:0;'>{''.join(pips)}</div>"
    )

    if label:
        return (
            f"<div style='display:inline-block;text-align:center;'>"
            f"<div style='font-size:14px;color:#ddd;margin-bottom:4px;'>{label}</div>"
            f"{pip_row}</div>"
        )
    return pip_row


class RatingResponse(HtmlKeyboardResponse):
    """Discrete N-point rating; works as response widget or static display.

    See module docstring for the two modes and when to use each.
    """

    def __init__(
        self,
        n_points=5,
        value=None,
        label=None,
        duration=None,
        side_effects=None,
    ):
        """
        Arguments:
            n_points (int): Number of discrete points on the scale, 2..10.
            value (int | None | Variable): If set, switches to display mode
                with `value` pips filled. If None, switches to response mode.
                May be a sweetbean Variable (e.g. TimelineVariable) to defer
                resolution until trial runtime.
            label (str | None): Optional caption shown above the pips.
            duration (int | None): Trial duration in ms.
                - Display mode: defaults to 1500 ms when None (so the trial
                  auto-advances). Pass an explicit value to override.
                - Response mode: defaults to None (waits for key press).
            side_effects (dict | None): Standard sweetbean side-effects.

        Emits (adds to jsPsych data):
            - bean_response (str | None): Pressed digit `'1'..'n_points'`
              in response mode; absent/None in display mode.
        """
        _validate_n_points(n_points)
        if isinstance(value, list):
            raise ValueError(
                "value must be an int, None, or a sweetbean Variable, not a list."
            )
        if not isinstance(value, Variable):
            _validate_value(value, n_points)

        is_display = value is not None and not isinstance(value, Variable)

        if is_display:
            choices = []
            effective_duration = duration if duration is not None else 1500
        else:
            # Response mode (value is None) — or Variable mode where we
            # don't know the value at construction; safer default is to
            # collect a response since a Variable usually means the value
            # is resolved per-trial.
            choices = [str(i) for i in range(1, n_points + 1)]
            effective_duration = duration

        stimulus = FunctionVariable(
            "rating_response_stimulus",
            render_rating_html,
            [value, n_points, label],
        )

        super().__init__(
            duration=effective_duration,
            stimulus=stimulus,
            choices=choices,
            correct_key="",
            side_effects=side_effects,
        )
        self.arg.update(
            {
                "n_points": n_points,
                "value": value,
                "label": label,
            }
        )
