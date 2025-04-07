import ast
import inspect
import textwrap


class TouchButton:
    """
    A class to create touch buttons as input instead of key presses
    (https://github.com/jspsych/jspsych-contrib/tree/main/packages/extension-touchscreen-buttons)
    """

    def __init__(self, key, layout):
        """
        Arguments:
            key: the key that is emulated by the touch button
            layout: the layout of the touch button
        """
        self.key = key
        self.layout = layout

    def to_js(self):
        return f'"{self.key}"'

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    @classmethod
    def left(cls, color=None):
        """
        Convenience Function to create a touch button on the left side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(key="l", layout={"key": "l", "color": color, "preset": "left"})

    @classmethod
    def right(cls, color=None):
        """
        Convenience Function to create a touch button on the right side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(key="r", layout={"key": "r", "color": color, "preset": "right"})

    @classmethod
    def bottom_left(cls, color=None):
        """
        Convenience Function to create a touch button on the bottom left side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(
            key="l", layout={"key": "l", "color": color, "preset": "bottom_left"}
        )

    @classmethod
    def bottom_right(cls, color=None):
        """
        Convenience Function to create a touch button on the bottom right side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(
            key="r", layout={"key": "r", "color": color, "preset": "bottom_right"}
        )

    @classmethod
    def top_left(cls, color=None):
        """
        Convenience Function to create a touch button on the top left side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(key="l", layout={"key": "l", "color": color, "preset": "top_left"})

    @classmethod
    def top_right(cls, color=None):
        """
        Convenience Function to create a touch button on the top right side of the screen
        """
        if color is None:
            color = "#fff"
        return cls(key="r", layout={"key": "r", "color": color, "preset": "top_right"})


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
