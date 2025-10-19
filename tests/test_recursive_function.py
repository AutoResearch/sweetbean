import os
import subprocess
import tempfile

from sweetbean import Block, Experiment
from sweetbean.stimulus import Fixation
from sweetbean.variable import FunctionVariable, TimelineVariable


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


def test_inner_functions():
    timeline = [{"a": 1, "b": 2}]

    def out_function(a):
        def inner_function(code):
            if code == 1:
                return 45
            if code == 2:
                return 135
            return 90  # neutral

        var_in = inner_function(a)
        return var_in

    var_out = FunctionVariable(
        name="patches", fct=out_function, args=[TimelineVariable("a")]
    )

    # stimuli
    fixation_1 = Fixation(duration=var_out)

    # build experiment
    block = Block([fixation_1], timeline=timeline)
    experiment = Experiment([block])
    experiment.to_js()
    js_code = f"let tst = {experiment.js}"
    valid, error_message = check_js_syntax(js_code)
    assert valid, f"JavaScript syntax error: {js_code}"


if __name__ == "__main__":
    test_inner_functions()
