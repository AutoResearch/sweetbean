import ast
import inspect
import io
import os
import re
import sys
import tempfile
import textwrap
from typing import Dict, List, Optional, Tuple

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


def _extract_lambda_only(src: str) -> str:
    """
    Return exactly the lambda expression from a source string that begins
    with 'lambda', even if extra call-site text follows (e.g., ', [...] )').
    Strategy: scan forward until the shortest prefix parses as an expression.
    """
    s = textwrap.dedent(src).lstrip()
    i = s.find("lambda")
    if i < 0:
        return s.strip()
    s = s[i:]  # start at 'lambda'
    for k in range(1, len(s) + 1):
        chunk = s[:k].strip()
        try:
            ast.parse(chunk, mode="eval")
            return chunk
        except SyntaxError:
            continue
    return s.strip()


def _emit_js_expr(node: ast.AST) -> str:
    """Very small emitter for simple lambda bodies used in FunctionVariable."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, str):
            return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
        if v is None:
            return "null"
        if isinstance(v, bool):
            return "true" if v else "false"
        return str(v)

    if isinstance(node, ast.Call):
        # str(x) -> String(x)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "str"
            and len(node.args) == 1
        ):
            return f"String({_emit_js_expr(node.args[0])})"
        # x.lower() -> (<x>).toLowerCase()
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "lower"
            and not node.args
        ):
            return f"({_emit_js_expr(node.func.value)}).toLowerCase()"
        # generic call
        f = _emit_js_expr(node.func)
        args = ",".join(_emit_js_expr(a) for a in node.args)
        return f"{f}({args})"

    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left = _emit_js_expr(node.left)
        right = _emit_js_expr(node.comparators[0])
        cmpop = node.ops[0]
        if isinstance(cmpop, ast.Eq):
            return f"({left}==={right})"
        if isinstance(cmpop, ast.NotEq):
            return f"({left}!={right})"
        if isinstance(cmpop, ast.Lt):
            return f"({left}<{right})"
        if isinstance(cmpop, ast.LtE):
            return f"({left}<={right})"
        if isinstance(cmpop, ast.Gt):
            return f"({left}>{right})"
        if isinstance(cmpop, ast.GtE):
            return f"({left}>={right})"

    if isinstance(node, ast.BoolOp):
        op_str = "&&" if isinstance(node.op, ast.And) else "||"
        return "(" + f" {op_str} ".join(_emit_js_expr(v) for v in node.values) + ")"

    if isinstance(node, ast.IfExp):
        return (
            f"({_emit_js_expr(node.test)}?{_emit_js_expr(node.body)}:"
            f"{_emit_js_expr(node.orelse)})"
        )

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return f"!({_emit_js_expr(node.operand)})"

    if isinstance(node, ast.BinOp) and isinstance(
        node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)
    ):
        ops = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%"}
        return f"({_emit_js_expr(node.left)}{ops[type(node.op)]}{_emit_js_expr(node.right)})"

    # Not a trivial form -> tell caller to fall back
    raise ValueError("expr-not-simple")


def _emit_simple_lambda_arrow(lambda_src: str) -> str:
    t_ast: ast.AST = ast.parse(lambda_src, mode="eval")
    node = t_ast.body if isinstance(t_ast, ast.Expression) else t_ast
    if not isinstance(node, ast.Lambda):
        node = _find_first_lambda_node(t_ast)
    params = [a.arg for a in node.args.args]  # type: ignore[union-attr]
    body_js = _emit_js_expr(node.body)  # type: ignore[union-attr]
    return f"(({','.join(params)})=>{{return {body_js}}})"


def _find_first_lambda_node(tree: ast.AST) -> ast.Lambda:
    for n in ast.walk(tree):
        if isinstance(n, ast.Lambda):
            return n
    raise ValueError("no-lambda-found")


def _emit_simple_lambda_arrow_from_node(lam: ast.Lambda) -> str:
    params = [a.arg for a in lam.args.args]
    body_js = _emit_js_expr(lam.body)  # your existing tiny emitter
    return f"(({','.join(params)})=>{{return {body_js}}})"


def _unparse(node: ast.AST) -> str:
    # Prefer stdlib (3.9+), else fall back, else raise with a clear hint
    try:  # stdlib
        from ast import unparse as _stdlib_unparse  # type: ignore[attr-defined]

        return _stdlib_unparse(node)  # type: ignore[misc]
    except Exception:
        try:  # astor
            import astor  # type: ignore

            return astor.to_source(node).rstrip()
        except Exception:
            try:  # astunparse
                import astunparse  # type: ignore

                return astunparse.unparse(node).rstrip()
            except Exception as e:
                raise RuntimeError(
                    "No AST unparser available. Install 'astor' or 'astunparse'."
                ) from e


def _build_wrapper_with_inner_def_from_node(lam: ast.Lambda, func) -> str:
    # Params of the lambda
    lam_params = []
    for a in lam.args.args:
        lam_params.append(a.arg)
    if lam.args.vararg:
        lam_params.append("*" + lam.args.vararg.arg)
    for a in lam.args.kwonlyargs:
        lam_params.append(a.arg)
    if lam.args.kwarg:
        lam_params.append("**" + lam.args.kwarg.arg)
    lam_params_str = ", ".join(lam_params)

    # Body of the lambda (as Python source)
    lam_body_str = _unparse(lam.body)

    # Outer wrapper params/call (preserve *args/**kwargs/defaults)
    sig = inspect.signature(func)
    params_list, call_list = [], []
    for name, p in sig.parameters.items():
        if p.kind is p.VAR_POSITIONAL:
            params_list.append(f"*{name}")
            call_list.append(f"*{name}")
        elif p.kind is p.VAR_KEYWORD:
            params_list.append(f"**{name}")
            call_list.append(f"**{name}")
        elif p.default is not p.empty:
            params_list.append(f"{name}={repr(p.default)}")
            call_list.append(name)
        else:
            params_list.append(name)
            call_list.append(name)
    outer_params_str = ", ".join(params_list)
    outer_call_str = ", ".join(call_list)

    # Nested def so Transcrypt emits a *local* function (no global `l`)
    return (
        f"def __sb_func__({outer_params_str}):\n"
        f"    def __lam({lam_params_str}):\n"
        f"        return {lam_body_str}\n"
        f"    return __lam({outer_call_str})\n"
    )


def _get_lambda_node_from_source(func) -> ast.Lambda:
    """
    Robustly obtain the lambda AST node from whatever source inspect returns,
    even if it’s embedded in a call expression or wrapped in parentheses.
    """
    src = textwrap.dedent(inspect.getsource(func)).strip()
    try:
        tree: ast.AST = ast.parse(src, mode="exec")
    except SyntaxError:
        tree = ast.parse(src, mode="eval")
    return _find_first_lambda_node(tree)


def _fct_to_js(func):
    """
    Convert a Python callable to a JavaScript arrow function string.

    - Uses Transcrypt for general cases.
    - Emits a pure JS arrow for simple lambdas.
    - Rejects non-local captures (except allowed modules).

    Examples (ellipses keep lines short):
    >>> def add(a, b): return a + b
    >>> _fct_to_js(add)
    '((a,b) => {return __add__(a,b)})'

    >>> _fct_to_js(lambda c: "f" if c == "red" else "j")
    "((c)=>{return ((c==='red')?'f':'j')})"

    >>> _fct_to_js(lambda s, n: f"Score: {s/n}")  # doctest: +ELLIPSIS
    '((s,n) => {...})'

    >>> def outer(v):
    ...     def inner(a):
    ...         if a == 1: return 45
    ...         if a == 2: return 135
    ...         return 90
    ...     return inner(v)
    >>> _fct_to_js(outer)  # doctest: +ELLIPSIS
    '((v) => {...})'


    """
    global_vars = func.__globals__
    code = func.__code__

    # Non-local checks (unchanged)
    non_locals = []
    for varname in code.co_names:
        if varname in global_vars and varname not in NON_LOCAL_INCLUDES:
            value = global_vars[varname]
            if isinstance(value, TouchButton):
                continue
            else:
                non_locals.append(varname)
    if non_locals:
        raise ValueError(
            f"Function:\n{inspect.getsource(func)}\n"
            f"contains non-local variables: {non_locals}.\n"
            f"Either the module is not supported or pass those values through "
            f"FunctionVariable args."
        )

    # Prepare a self-contained Python module for Transcrypt
    try:
        source_code = inspect.getsource(func)
        source_code = textwrap.dedent(source_code).strip()
        func_name_for_extract = None

        if func.__name__ == "<lambda>":
            # 1) Get the lambda node from the full, raw source
            lam_node = _get_lambda_node_from_source(func)

            # 2) Try the fast path: emit pure JS arrow (no Transcrypt, no `l`)
            try:
                return _emit_simple_lambda_arrow_from_node(lam_node)
            except Exception:
                pass  # Not a simple expression → fall back

            # 3) Fallback: nested-def wrapper to avoid any hoisted helper
            wrapper_src = _build_wrapper_with_inner_def_from_node(lam_node, func)
            tree = ast.parse(wrapper_src)
            func_name_for_extract = "__sb_func__"
        else:
            # Normal def: compile as-is
            tree = ast.parse(source_code)
            func_name_for_extract = func.__name__

        # Reserved-word arg renaming, operator lowering, TouchButton replacer (unchanged)
        tree = _JSReservedArgRenamer().visit(tree)
        ast.fix_missing_locations(tree)
        source_code = _unparse(tree)
        source_code = replace_operators_with_functions(source_code)
        tree = ast.parse(source_code)
        tree = _TouchButtonReplacer({}).visit(tree)
        ast.fix_missing_locations(tree)
        source_code = _unparse(tree)

    except Exception as e:
        raise Exception(f"Error during conversion: {e}") from e

    # Transcrypt pipeline (unchanged)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, "temp_script.py")
        with open(temp_path, "w") as f:
            f.write(source_code)

        old_cwd, old_argv = os.getcwd(), sys.argv[:]
        output_buffer = io.StringIO()
        try:
            os.chdir(temp_dir)
            sys.argv = [sys.argv[0], "-b", "temp_script.py"]
            saved_stdout = sys.stdout
            sys.stdout = output_buffer
            exit_code = transcrypt_main()
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)
            sys.stdout = saved_stdout

        if exit_code != 0:
            error_output = output_buffer.getvalue() or "No detailed error provided."
            raise RuntimeError(
                f"Error occurred during execution. Return code: {exit_code}.\n"
                f"Output: {error_output}."
            )

        js_output_path = os.path.join(temp_dir, "__target__", "temp_script.js")
        if not os.path.exists(js_output_path):
            raise FileNotFoundError(f"JavaScript file not found: {js_output_path}")

        with open(js_output_path, "r") as f:
            full_js_code = f.read()

    # IMPORTANT: don’t strip "__lambda__" here
    arrow = _extract_arrow_function(full_js_code, func_name_for_extract)
    # Optional postprocessing (your existing helper)
    return _postprocess_functions(arrow)


def _extract_arrow_function(js_code: str, func_name: Optional[str] = None):
    js_code = _clean_function(js_code)

    # Prefer to find the requested binding name
    starts = []
    if func_name and func_name != "<lambda>":
        n = re.escape(func_name)
        starts = [
            rf"(?:export\s+)?var\s+{n}\s*=\s*function\s*\(",
            rf"(?:export\s+)?let\s+{n}\s*=\s*function\s*\(",
            rf"(?:export\s+)?const\s+{n}\s*=\s*function\s*\(",
            rf"{n}\s*=\s*function\s*\(",
            rf"(?:export\s+)?function\s+{n}\s*\(",  # named function declaration
        ]
        start_idx = _find_first(js_code, starts)
    else:
        # Fallback: first top-level binding
        starts = [
            r"(?:export\s+)?var\s+[A-Za-z_$][\w$]*\s*=\s*function\s*\(",
            r"(?:export\s+)?let\s+[A-Za-z_$][\w$]*\s*=\s*function\s*\(",
            r"(?:export\s+)?const\s+[A-Za-z_$][\w$]*\s*=\s*function\s*\(",
            r"(?:export\s+)?function\s+[A-Za-z_$][\w$]*\s*\(",
        ]
        start_idx = _find_first(js_code, starts)

    if start_idx is None:
        # Last-resort fallback
        m = re.search(r"function\s*\(", js_code)
        if not m:
            raise RuntimeError("Could not locate a compiled function binding.")
        start_idx = m.start()

    # Read the parameter list and body
    func_paren = js_code.find("(", start_idx)
    if func_paren == -1:
        raise RuntimeError("Malformed function: missing '(' after binding.")

    params, after_params = _read_balanced(js_code, func_paren, "(", ")")

    i = after_params
    while i < len(js_code) and js_code[i].isspace():
        i += 1
    if i >= len(js_code) or js_code[i] != "{":
        raise RuntimeError("Malformed function: expected '{' after parameter list.")

    body, _ = _read_balanced(js_code, i, "{", "}")

    # Build an IIFE-ready arrow expression by wrapping the whole thing in extra parens.
    params = params[1:-1]  # strip the surrounding ()
    arrow_core = f"({params}) => {body}"
    iife_ready = f"({arrow_core})"
    return _postprocess_functions(iife_ready)


def _find_first(s: str, patterns: List[str]) -> Optional[int]:
    best = None
    for pat in patterns:
        m = re.search(pat, s)
        if m:
            pos = s.find("function", m.start())
            if pos != -1 and (best is None or pos < best):
                best = pos
    return best


def _read_balanced(
    s: str, start_idx: int, open_char: str, close_char: str
) -> Tuple[str, int]:
    """
    Return (substring_including_delims, index_after_substring) for (), {}, [] starting at start_idx.
    Handles quotes/backticks/escapes so braces in strings don't break parsing.
    """
    assert s[start_idx] == open_char
    i = start_idx
    depth = 0
    in_str: Optional[str] = None
    esc = False
    while i < len(s):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ("'", '"', "`"):
            in_str = ch
            i += 1
            continue
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                i += 1
                return s[start_idx:i], i
        i += 1
    raise RuntimeError(f"Unbalanced {open_char}{close_char} starting at {start_idx}")


def _clean_function(js_code):
    # do light whitespace/format normalization only
    res = js_code.replace("= function", "=function")
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


JS_RESERVED_WORDS = {
    # ES keywords + strict mode + future (core set; extend if needed)
    "var",
    "let",
    "const",
    "function",
    "class",
    "default",
    "enum",
    "export",
    "import",
    "extends",
    "super",
    "return",
    "if",
    "else",
    "switch",
    "case",
    "break",
    "new",
    "for",
    "while",
    "do",
    "try",
    "catch",
    "finally",
    "with",
    "yield",
    "await",
    "this",
    "delete",
    "in",
    "instanceof",
    "typeof",
    "void",
    "of",
    "public",
    "private",
    "protected",
    "static",
    "package",
    "interface",
    "implements",
}


class _JSReservedArgRenamer(ast.NodeTransformer):
    """
    Renames any function/lambda parameter that collides with a JS reserved word.
    Updates all references within the function body (including inner functions)
    by tracking nested scopes on a stack.
    """

    def __init__(self, suffix: str = "_py"):
        super().__init__()
        self._stack: List[Dict[str, str]] = []
        self._suffix = suffix

    def _maybe_rename_arg(self, arg: ast.arg) -> None:
        if arg and arg.arg in JS_RESERVED_WORDS:
            new_name = f"{arg.arg}{self._suffix}"
            # record mapping in current scope
            self._stack[-1][arg.arg] = new_name
            arg.arg = new_name

    def _push_scope(self) -> None:
        self._stack.append({})

    def _pop_scope(self) -> None:
        self._stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self._push_scope()
        # positional args
        for a in node.args.args:
            self._maybe_rename_arg(a)
        # *args
        if node.args.vararg:
            self._maybe_rename_arg(node.args.vararg)
        # keyword-only args
        for a in node.args.kwonlyargs:
            self._maybe_rename_arg(a)
        # **kwargs
        if node.args.kwarg:
            self._maybe_rename_arg(node.args.kwarg)

        # visit defaults/annotations/body with mapping active
        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        self._push_scope()
        for a in node.args.args:
            self._maybe_rename_arg(a)
        if node.args.vararg:
            self._maybe_rename_arg(node.args.vararg)
        for a in node.args.kwonlyargs:
            self._maybe_rename_arg(a)
        if node.args.kwarg:
            self._maybe_rename_arg(node.args.kwarg)
        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        for scope in reversed(self._stack):
            if node.id in scope:
                node.id = scope[node.id]
                break
        return node
