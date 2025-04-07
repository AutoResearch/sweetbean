import ast
import inspect
import textwrap


class TouchButton:
    """ """

    def __init__(self, key, layout):
        self.key = key
        self.layout = layout

    def to_js(self):
        return f'"{self.key}"'

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    @classmethod
    def left(cls):
        return cls(
            key="l", layout={"key": "l", "color": "#fff", "preset": "bottom_left"}
        )

    @classmethod
    def right(cls):
        return cls(
            key="r", layout={"key": "r", "color": "#fff", "preset": "bottom_right"}
        )


# TouchButton.Left = TouchButton.left()
# TouchButton.Right = TouchButton.right()


class _TouchButtonReplacer(ast.NodeTransformer):
    def __init__(self, replacements):
        self.replacements = replacements

    def visit_Name(self, node):
        # Replace global variables like LEFT, RIGHT
        if node.id in self.replacements:
            return ast.copy_location(
                ast.Constant(value=self.replacements[node.id]), node
            )
        return node

    def visit_Call(self, node):
        # Replace calls like TouchButton.left() or TouchButton.right()
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "TouchButton"
            ):
                method_name = node.func.attr
                if method_name == "left":
                    return ast.copy_location(ast.Constant(value="l"), node)
                elif method_name == "right":
                    return ast.copy_location(ast.Constant(value="r"), node)
        return self.generic_visit(node)


def collect_touch_buttons_from_function(func):
    buttons = set()

    try:
        source = inspect.getsource(func)
        source = textwrap.dedent(source)
        tree = ast.parse(source)

        class TouchButtonConstructorFinder(ast.NodeVisitor):
            def visit_Call(self, node):
                try:
                    # Match direct constructor: TouchButton(...)
                    if (
                        isinstance(node.func, ast.Name)
                        and node.func.id == "TouchButton"
                    ):
                        compiled = compile(
                            ast.Expression(body=node), filename="<ast>", mode="eval"
                        )
                        value = eval(compiled, func.__globals__)
                        if isinstance(value, TouchButton):
                            buttons.add(value)

                    # Match any TouchButton.xxx() call (generic method)
                    elif (
                        isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "TouchButton"
                    ):
                        compiled = compile(
                            ast.Expression(body=node), filename="<ast>", mode="eval"
                        )
                        value = eval(compiled, func.__globals__)
                        if isinstance(value, TouchButton):
                            buttons.add(value)

                except Exception as e:
                    print(f"[TouchButton AST eval error]: {e}")
                self.generic_visit(node)

        TouchButtonConstructorFinder().visit(tree)

    except Exception as e:
        print(f"[TouchButton parse error]: {e}")

    return buttons
