from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse
from sweetbean.variable import FunctionVariable, Variable


FEATURE_NAMES = (
    "shape",
    "color",
    "size",
    "border",
    "pattern",
    "inner_mark",
)

FEATURE_VALUES = {
    "shape": {0: "circle", 1: "triangle"},
    "color": {0: "orange", 1: "blue"},
    "size": {0: "small", 1: "large"},
    "border": {0: "none", 1: "pink border"},
    "pattern": {0: "filled", 1: "striped"},
    "inner_mark": {0: "none", 1: "star"},
}


def _validate_feature_vector(feature_vector):
    if not isinstance(feature_vector, list):
        raise ValueError("feature_vector must be a list with up to 6 binary values.")
    if len(feature_vector) == 0:
        raise ValueError("feature_vector must contain at least one feature value.")
    if len(feature_vector) > 6:
        raise ValueError("feature_vector can contain at most 6 feature values.")
    for i, value in enumerate(feature_vector):
        if value not in (0, 1):
            raise ValueError(
                f"feature_vector[{i}] must be 0 or 1, got {value!r}."
            )


def _decode_feature_vector(feature_vector):
    _validate_feature_vector(feature_vector)
    decoded = {}
    for index, value in enumerate(feature_vector):
        feature_name = FEATURE_NAMES[index]
        decoded[feature_name] = FEATURE_VALUES[feature_name][value]
    return decoded


def _feature_vector_to_description(feature_vector):
    n = len(feature_vector)
    shape = "triangle" if n >= 1 and feature_vector[0] == 1 else "circle"
    color = "blue" if n >= 2 and feature_vector[1] == 1 else "orange"
    size = "large" if n >= 3 and feature_vector[2] == 1 else "small"
    border = "pink border" if n >= 4 and feature_vector[3] == 1 else "none"
    pattern = "striped" if n >= 5 and feature_vector[4] == 1 else "filled"
    inner_mark = "star" if n >= 6 and feature_vector[5] == 1 else "none"

    parts = []
    if n >= 3:
        parts.append(size)
    if n >= 2:
        parts.append(color)
    if n >= 5:
        parts.append(pattern)
    if n >= 1:
        parts.append(shape)

    description = " ".join(parts).strip()
    if not description:
        description = "object"
    if border == "pink border":
        description += " with a pink border"
    if inner_mark == "star":
        description += " with a star inside"
    return description


def _feature_vector_to_html(feature_vector):
    # Literals only — Transcrypt rejects non-local globals (FunctionVariable / _fct_to_js).
    _circle_border_px = 13

    n = len(feature_vector)
    shape = "triangle" if n >= 1 and feature_vector[0] == 1 else "circle"
    color = "blue" if n >= 2 and feature_vector[1] == 1 else "orange"
    size = "large" if n >= 3 and feature_vector[2] == 1 else "small"
    border = (
        "pink border" if n >= 4 and feature_vector[3] == 1 else "none"
    )
    pattern = "striped" if n >= 5 and feature_vector[4] == 1 else "filled"
    inner_mark = "star" if n >= 6 and feature_vector[5] == 1 else "none"

    pixel_size = 240 if size == "large" else 90
    # Colorblind-friendly palette (Wong / Okabe–Ito style)
    css_color = "#0072B2" if color == "blue" else "#E69F00"
    if pattern == "striped":
        background_css = (
            "repeating-linear-gradient(45deg, "
            f"{css_color}, {css_color} 10px, "
            "rgba(255,255,255,0.45) 10px, rgba(255,255,255,0.45) 20px)"
        )
    else:
        background_css = css_color

    star_html = ""
    if inner_mark == "star":
        star_html = (
            "<div style='position:absolute;top:50%;left:50%;"
            "transform:translate(-50%,-50%);font-size:36px;"
            "line-height:1;color:#ffffff;text-shadow:0 0 3px #000;'"
            ">★</div>"
        )

    shell = (
        "display:flex;justify-content:center;align-items:center;height:100%;"
    )

    if shape == "circle":
        border_css = (
            f"{_circle_border_px}px solid #CC79A7"
            if border == "pink border"
            else "none"
        )
        inner = (
            f"<div style='box-sizing:border-box;position:relative;width:{pixel_size}px;"
            f"height:{pixel_size}px;background:{background_css};border:{border_css};"
            f"border-radius:50%;'>{star_html}</div>"
        )
        return f"<div style='{shell}'>{inner}</div>"

    # Triangle: SVG stroke is even along the path; pad viewBox so stroke is not clipped
    # at corners (stroke draws past the path; viewBox 0–100 cuts it off without margin).
    # Match circle's border thickness (13 px) so both shapes read as "bordered" equally.
    _sw = str(_circle_border_px) if border == "pink border" else "0"
    _sc = "#CC79A7" if border == "pink border" else "none"
    if pattern == "striped":
        _defs = (
            "<defs><pattern id='sbclstrp' patternUnits='userSpaceOnUse' width='20' height='20' "
            "patternTransform='rotate(45)'><rect width='10' height='20' "
            f"fill='{css_color}'/><rect x='10' width='10' height='20' "
            "fill='rgba(255,255,255,0.45)'/></pattern></defs>"
        )
        _fill = "url(#sbclstrp)"
    else:
        _defs = ""
        _fill = css_color

    # ~24 user units padding: room for the thicker stroke (~13 px) at apex and base corners.
    tri = (
        f"<div style='position:relative;width:{pixel_size}px;height:{pixel_size}px;"
        "overflow:visible;'>"
        f"<svg width='{pixel_size}' height='{pixel_size}' "
        "viewBox='-24 -24 148 148' preserveAspectRatio='xMidYMid meet' "
        "style='overflow:visible;display:block;'>"
        f"{_defs}<polygon points='50,0 0,100 100,100' fill='{_fill}' stroke='{_sc}' "
        f"stroke-width='{_sw}' stroke-linejoin='round' stroke-linecap='round' "
        "paint-order='stroke fill' vector-effect='non-scaling-stroke' /></svg>"
        f"{star_html}</div>"
    )
    return f"<div style='{shell}'>{tri}</div>"


class DefaultCategoryLearning(HtmlKeyboardResponse):
    """
    Category-learning stimulus based on a binary feature vector.

    Feature order:
      0 shape      (0 circle, 1 triangle)
      1 color      (0 orange #E69F00, 1 blue #0072B2)
      2 size       (0 small, 1 large)
      3 border     (0 none, 1 pink #CC79A7)
      4 pattern    (0 filled, 1 striped)
      5 inner_mark (0 none, 1 star)
    """

    l_template = "You see a {{ feature_description }}."

    def __init__(
        self,
        duration=None,
        feature_vector=None,
        choices=None,
        correct_key="",
        prompt_template=None,
        response_template=None,
        side_effects=None,
    ):
        if feature_vector is None:
            raise ValueError("feature_vector is required for DefaultCategoryLearning.")
        # TimelineVariable / other Variables are resolved at runtime; validate then.
        if isinstance(feature_vector, list):
            _validate_feature_vector(feature_vector)
        elif not isinstance(feature_vector, Variable):
            raise ValueError(
                "feature_vector must be a list of 0/1 values or a SweetBean Variable "
                "(e.g. TimelineVariable('feature_vector'))."
            )
        stimulus = FunctionVariable(
            "default_category_learning_stimulus",
            _feature_vector_to_html,
            [feature_vector],
        )
        feature_description = FunctionVariable(
            "default_category_learning_description",
            _feature_vector_to_description,
            [feature_vector],
        )
        super().__init__(
            duration=duration,
            stimulus=stimulus,
            choices=choices,
            correct_key=correct_key,
            side_effects=side_effects,
        )
        if prompt_template is not None:
            self.l_template = prompt_template
        if response_template is not None:
            self.response_template = response_template
        self.arg.update(
            {
                "feature_vector": feature_vector,
                "feature_description": feature_description,
            }
        )
