import ast
import inspect
import io
import os
import re
import sys
import tempfile
import textwrap

from transcrypt.__main__ import main as transcrypt_main

from sweetbean.extension.TouchButton import TouchButton, _TouchButtonReplacer


def to_js(var):
    return _var_to_js(var)


NON_LOCAL_INCLUDES = [
    "math",
    "random",
    "numpy",
    "pandas",
    "datetime",
    "time",
    "re",
    "os",
    "sys",
    "json",
    "csv",
    "TouchButton",
]


def _fct_args_to_js(args):
    """
    Convert Python argument list to JavaScript inputs for a function.
    Examples:

    """
    res = "("
    for idx, arg in enumerate(args):
        res += str(_var_to_js(arg))
        if idx != len(args) - 1:
            res += ", "
    res += ")"
    return res


def _var_to_js(var):
    """
    Convert a python input value to a JavaScript input value.
    """
    if var is None:
        return "null"
    if isinstance(var, str):
        _var = var.replace("'", "\\'")
        return f"'{_var}'"
    # test if is sequence
    if (
        isinstance(var, (list, tuple, set))
        or type(var) is {}.keys().__class__
        or type(var) is {}.values().__class__
    ):
        res = "["
        for idx, v in enumerate(var):
            res += str(_var_to_js(v))
            if idx != len(var) - 1:
                res += ","
        return f"{res}]"
    if isinstance(var, dict):
        res = "{"
        for k, v in var.items():
            res += f"'{k}': {_var_to_js(v)}"
            if k != list(var.keys())[-1]:
                res += ","
        return f"{res}}}"
    if isinstance(var, bool):
        return str(var).lower()
    if hasattr(var, "to_js"):
        return var.to_js()
    return var


def _fct_to_js(func):
    """
    Convert a Python function to JavaScript using Transcrypt, without using subprocess.

    Examples:
    # >>> def add(a, b):
    # ...     return a + b
    # >>> _fct_to_js(add)
    # '(a,b) => {return a+b}'

    >>> a = lambda color: "f" if color == "red" else "j"
    >>> _fct_to_js(a)
    '(color) => {return __eq__(color,"red")?"f":"j"}'

    >>> b = lambda score, n: f"Score: {score/n}"
    >>> _fct_to_js(b)
    '(score,n) => {return"Score: {}".format(__truediv__(score,n))}'

    """
    global_vars = func.__globals__
    code = func.__code__

    # Find variables used in the function but not defined locally
    non_locals = []
    replacements = {}
    for varname in code.co_names:
        if varname in global_vars and varname not in NON_LOCAL_INCLUDES:
            value = global_vars[varname]
            if isinstance(value, TouchButton):
                continue
            else:
                non_locals.append(varname)

    if non_locals:
        raise ValueError(
            f"Function:\n"
            f"{inspect.getsource(func)}\n"
            f"contains non-local variables: {non_locals}.\n"
            f"Either the module is not supported "
            f"or the variable should be passed into "
            f"the FunctionVariable instead."
        )

    # Extract and pre-process the function's source
    try:
        source_code = inspect.getsource(func)
        source_code = textwrap.dedent(source_code)
        source_code = replace_operators_with_functions(source_code)

        tree = ast.parse(source_code)
        tree = _TouchButtonReplacer(replacements).visit(tree)
        ast.fix_missing_locations(tree)
        source_code = ast.unparse(tree)

    except Exception as e:
        raise Exception(f"Error during conversion: {e}") from e

    # Use a temporary directory to store the necessary files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, "temp_script.py")

        # Write the function's source code to a temporary Python file
        with open(temp_path, "w") as temp_file:
            temp_file.write(source_code)

        if not os.path.exists(temp_path):
            raise FileNotFoundError(f"Temporary file not found at: {temp_path}")

        # Call Transcrypt directly, avoiding subprocess
        old_cwd = os.getcwd()
        old_argv = sys.argv[:]
        output_buffer = io.StringIO()
        try:
            os.chdir(temp_dir)
            # Replace sys.argv so Transcrypt reads the same flags as subprocess
            sys.argv = [sys.argv[0], "-b", "temp_script.py"]

            # Capture Transcrypt's console output
            saved_stdout = sys.stdout
            sys.stdout = output_buffer

            exit_code = transcrypt_main()

        finally:
            # Restore environment
            sys.argv = old_argv
            os.chdir(old_cwd)
            sys.stdout = saved_stdout

        # Check if Transcrypt failed
        if exit_code != 0:
            error_output = output_buffer.getvalue()
            if not error_output:
                error_output = "No detailed error provided."
            raise RuntimeError(
                f"Error occurred during execution. Return code: {exit_code}.\n"
                f"Output: {error_output}."
            )

        # Locate the JavaScript output in the __target__ folder
        js_output_dir = os.path.join(temp_dir, "__target__")
        js_output_path = os.path.join(js_output_dir, "temp_script.js")

        if not os.path.exists(js_output_path):
            raise FileNotFoundError(f"JavaScript file not found: {js_output_path}")

        # Read the full JavaScript code
        with open(js_output_path, "r") as js_file:
            full_js_code = js_file.read()

    # Finally, parse out the final arrow function from the compiled JS
    return _extract_arrow_function(full_js_code)


def _extract_arrow_function(js_code):
    js_code = _clean_function(js_code)

    match = re.search(r"function\((.*?)\)\{(.*?)\};", js_code, re.DOTALL)
    if not match:
        match = re.search(r"function\((.*?)\)\{(.*?)\},", js_code, re.DOTALL)
    if not match:
        match = re.search(r"function\((.*?)\)\{(.*?)\}", js_code, re.DOTALL)

    if match:
        # Convert to an arrow function
        params = match.group(1)
        body = match.group(2).strip()
        arrow_function = f"({params}) => {{{body}}}"
        # arrow_function = _postprocess_format(arrow_function)
        arrow_function = _postprocess_functions(arrow_function)
        return arrow_function


def _clean_function(js_code):
    res = js_code.replace("__lambda__", "")
    res = res.replace("= function", "=function")
    res = res.replace("function (", "function(")
    res = res.replace(") =", ")=")
    return res


def _postprocess_format(js_code):
    """
    Replace `.format(...)` calls in the generated JavaScript
    with equivalent JavaScript template literals.

    Examples:
        >>> function = '(score,n) => {return"Score: {}".format(__truediv__(score,n))}'
        >>> _postprocess_format(function)
        '(score,n) => {return`Score: ${__truediv__(score,n)}`}'
    """
    import re

    # Match any string with `.format(...)`
    pattern = r'(["\'].*?\{.*?\}.*?["\'])\.format\((.*)\)'

    def replacer(match):
        """
        Replace `.format(...)` calls with JavaScript-compatible template literals.
        """
        # Extract the string template and the arguments
        template = match.group(1).strip()  # The string with placeholders (quoted)
        _inpt = match.group(2)
        # ]  # The replacement arguments
        arguments = _split_outer_commas(_inpt)
        # Remove the surrounding quotes and replace `{}` with `${...}`
        lst = template[-1]
        for i, arg in enumerate(template):
            j = i + 2
            candidate = template[-j]
            if candidate == lst:
                start = template[:-j] + "`"
                end = template[-j + 1 : -1] + "`"
                template = start + end
                break
        # template = template[1:-1]  # Strip the first and last character (quotes)
        for i, arg in enumerate(arguments):
            template = template.replace(
                "{}", f"${{{arg}}}", 1
            )  # Replace one placeholder at a time

        # Convert the modified string to a JavaScript template literal
        return f"{template}"

    # Replace all `.format(...)` calls in the JavaScript code
    js_code = re.sub(pattern, replacer, js_code)
    js_code = js_code.replace(".format()", "")
    return js_code


def _split_outer_commas(input_str):
    result = []
    current = []
    depth = 0  # Track depth of parentheses

    for char in input_str:
        if char == "," and depth == 0:  # Split only when at depth 0
            result.append("".join(current).strip())
            current = []
        else:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            current.append(char)

    # Append the last group
    if current:
        result.append("".join(current).strip())

    return result


def _postprocess_functions(js_code):
    """
    Replace known Python functions with their JavaScript equivalents.
    """
    # Define patterns and replacements
    replacements = {
        r"random\.randint\((.*?)\)": r"Math.floor(Math.random() * [\1][1]) - [\1][0] + 1",
        r"math.": r"Math.",
    }

    # Process replacements dynamically
    for py_function, js_function in replacements.items():
        js_code = re.sub(py_function, js_function, js_code)

    return js_code


OPERATOR_TO_FUNCTION = {
    ast.Add: "__add__",
    ast.Sub: "__sub__",
    ast.Mult: "__mul__",
    ast.Div: "__truediv__",
    ast.Mod: "__mod__",
    ast.Pow: "__pow__",
    ast.LShift: "__lshift__",
    ast.RShift: "__rshift__",
    ast.BitOr: "__or__",
    ast.BitXor: "__xor__",
    ast.BitAnd: "__and__",
    ast.FloorDiv: "__floordiv__",
    ast.MatMult: "__matmul__",
    ast.Eq: "__eq__",
    ast.NotEq: "__ne__",
    ast.Lt: "__lt__",
    ast.LtE: "__le__",
    ast.Gt: "__gt__",
    ast.GtE: "__ge__",
}


class ReplaceOperatorsWithFunctions(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        operator_type = type(node.op)
        if operator_type in OPERATOR_TO_FUNCTION:
            func_name = OPERATOR_TO_FUNCTION[operator_type]
            new_node = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[],
            )
            return ast.copy_location(new_node, node)
        else:
            return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        operator_type = type(node.op)
        if operator_type in OPERATOR_TO_FUNCTION:
            func_name = OPERATOR_TO_FUNCTION[operator_type]
            new_node = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[node.operand],
                keywords=[],
            )
            return ast.copy_location(new_node, node)
        else:
            return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1:
            operator_type = type(node.ops[0])
            if operator_type in OPERATOR_TO_FUNCTION:
                func_name = OPERATOR_TO_FUNCTION[operator_type]
                new_node = ast.Call(
                    func=ast.Name(id=func_name, ctx=ast.Load()),
                    args=[node.left, node.comparators[0]],
                    keywords=[],
                )
                return ast.copy_location(new_node, node)
        else:
            # Handle chained comparisons
            comparisons = []
            left = node.left
            for op, right in zip(node.ops, node.comparators):
                operator_type = type(op)
                if operator_type in OPERATOR_TO_FUNCTION:
                    func_name = OPERATOR_TO_FUNCTION[operator_type]
                    comparison = ast.Call(
                        func=ast.Name(id=func_name, ctx=ast.Load()),
                        args=[left, right],
                        keywords=[],
                    )
                    comparisons.append(comparison)
                    left = right
                else:
                    return node
            # Combine comparisons with 'and_'
            combined = comparisons[0]
            for comp in comparisons[1:]:
                combined = ast.Call(
                    func=ast.Name(id="and_", ctx=ast.Load()),
                    args=[combined, comp],
                    keywords=[],
                )
            return ast.copy_location(combined, node)
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        operator_type = type(node.op)
        if operator_type in OPERATOR_TO_FUNCTION:
            func_name = OPERATOR_TO_FUNCTION[operator_type]
            # Since 'and' and 'or' are variable-length operators, we need to combine the values
            values = node.values
            combined = values[0]
            for value in values[1:]:
                combined = ast.Call(
                    func=ast.Name(id=func_name, ctx=ast.Load()),
                    args=[combined, value],
                    keywords=[],
                )
            return ast.copy_location(combined, node)
        else:
            return node

    def visit(self, node):
        return super().visit(node)


def replace_operators_with_functions(code):
    tree = ast.parse(code)
    transformer = ReplaceOperatorsWithFunctions()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return ast.unparse(transformed_tree)
