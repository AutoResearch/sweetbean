from sweetbean.stimulus.HtmlKeyboardResponse import HtmlKeyboardResponse
from sweetbean.variable import FunctionVariable


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
    "color": {0: "red", 1: "blue"},
    "size": {0: "small", 1: "large"},
    "border": {0: "none", 1: "black border"},
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
    decoded = _decode_feature_vector(feature_vector)
    parts = []
    if "size" in decoded:
        parts.append(decoded["size"])
    if "color" in decoded:
        parts.append(decoded["color"])
    if "pattern" in decoded:
        parts.append(decoded["pattern"])
    if "shape" in decoded:
        parts.append(decoded["shape"])

    suffix_parts = []
    if decoded.get("border") == "black border":
        suffix_parts.append("with a black border")
    if decoded.get("inner_mark") == "star":
        suffix_parts.append("with a star inside")

    description = " ".join(parts).strip()
    if not description:
        description = "object"
    if suffix_parts:
        description = f"{description} " + " ".join(suffix_parts)
    return description


def _feature_vector_to_html(feature_vector):
    decoded = _decode_feature_vector(feature_vector)
    size = decoded.get("size", "small")
    color = decoded.get("color", "red")
    shape = decoded.get("shape", "circle")
    pattern = decoded.get("pattern", "filled")
    border = decoded.get("border", "none")
    inner_mark = decoded.get("inner_mark", "none")

    pixel_size = 180 if size == "large" else 120
    css_color = "#1f77b4" if color == "blue" else "#d62728"
    shape_css = "border-radius: 50%;" if shape == "circle" else "clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"
    border_css = "4px solid #000000" if border == "black border" else "none"
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

    return (
        "<div style='display:flex;justify-content:center;align-items:center;height:100%;'>"
        f"<div style='position:relative;width:{pixel_size}px;height:{pixel_size}px;"
        f"background:{background_css};border:{border_css};{shape_css}'>"
        f"{star_html}</div></div>"
    )


class DefaultCategoryLearning(HtmlKeyboardResponse):
    """
    Category-learning stimulus based on a binary feature vector.

    Feature order:
      0 shape      (0 circle, 1 triangle)
      1 color      (0 red, 1 blue)
      2 size       (0 small, 1 large)
      3 border     (0 none, 1 black border)
      4 pattern    (0 filled, 1 striped)
      5 inner_mark (0 none, 1 star)
    """

    l_template = (
        "You see a <{{ feature_description }}>"
        "{% if duration %} for {{duration}}ms{% endif %}."
    )

    def __init__(
        self,
        duration=None,
        feature_vector=None,
        choices=None,
        correct_key="",
        side_effects=None,
    ):
        if feature_vector is None:
            raise ValueError("feature_vector is required for DefaultCategoryLearning.")
        _validate_feature_vector(feature_vector)
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
        self.arg.update(
            {
                "feature_vector": feature_vector,
                "feature_description": feature_description,
            }
        )
