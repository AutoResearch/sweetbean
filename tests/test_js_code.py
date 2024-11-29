import os
import random
import subprocess
import tempfile

from sweetbean_v2.datatype.variables import (
    DataVariable,
    FunctionVariable,
    TimelineVariable,
)
from sweetbean_v2.stimulus.Stimulus import _BaseStimulus


def test_stimulus():
    """
    Test if the generated JavaScript code has valid syntax.
    """

    # generate a list of different types of variables
    variables = [
        1,
        100,  # int
        "a",
        "Hello",
        "@em**",
        ". / { ",
        False,
        True,
        [1, 2, 3],
        ["a", "b", "c"],
        ["a", 1, "b"],
        TimelineVariable("a"),
        TimelineVariable("a b c"),
        DataVariable("a", 1),
        [TimelineVariable("a"), TimelineVariable("b")],
        [TimelineVariable("a"), DataVariable("b", 3)],
    ]

    def generate_stimulus_single(arg):
        """
        Generate a stimulus with a list of variables.
        """
        stimulus = _BaseStimulus({"a": arg})
        js = f"let tst = {stimulus.js}"
        return js

    def generate_stimulus_double(a, b):
        """
        Generate a stimulus with a list of variables.
        """
        stimulus = _BaseStimulus({"a": a, "b": b})
        js = f"let tst = {stimulus.js}"
        return js

    # get a subset of variables
    for variable_0 in variables:
        js_code = generate_stimulus_single(variable_0)
        valid, error_message = check_js_syntax(js_code)
        assert valid, f"JavaScript syntax error: {error_message}"

    for variable_0 in random.choices(variables, k=3):
        for variable_1 in random.choices(variables, k=3):
            js_code = generate_stimulus_double(variable_0, variable_1)
            valid, error_message = check_js_syntax(js_code)
            assert valid, f"JavaScript syntax error: {error_message}"

    # test with a function

    def add(a, b):
        for _ in range(100):
            a += b
        return a + b

    d = DataVariable("a", 1)
    t = TimelineVariable("b")

    f = FunctionVariable("f", add, [d, t])

    stimulus = _BaseStimulus({"dataVar": d, "timeVar": t, "fctVar": f})
    js = f"let tst = {stimulus.js}"
    valid, error_message = check_js_syntax(js)
    assert valid, f"JavaScript syntax error: {error_message}"


def check_js_syntax(js_code):
    """
    Check JavaScript syntax for errors using Node.js without executing the code.
    """
    try:
        # Write the JavaScript code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as temp_file:
            temp_file.write(js_code.encode())
            temp_path = temp_file.name

        # Run Node.js in syntax-check mode
        result = subprocess.run(
            ["node", "--check", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Clean up the temporary file
        os.remove(temp_path)

        # Check the result
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, None
    except FileNotFoundError:
        raise RuntimeError("Node.js is required for syntax checking.")
