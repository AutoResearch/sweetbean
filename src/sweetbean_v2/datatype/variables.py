from abc import ABC, abstractmethod

from sweetbean_v2.datatype.js_parser import _fct_args_to_js, _fct_to_js, _var_to_js


def to_js(var):
    return _var_to_js(var)


class Variable(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def to_js(self):
        pass


class TimelineVariable(Variable):
    """
    A timeline variable for jsPsych.
    """

    def to_js(self):
        return f"jsPsych.timelineVariable('{self.name}')"


class DataVariable(Variable):
    """
    A data variable for jsPsych to access data of previous trials.
    """

    def __init__(self, name, window):
        super().__init__(name)
        self.name = f'data["bean_{name}"]'
        self.raw_name = name
        self.window = window

    def to_js(self):
        if self.window == 0:
            return self.name
        return f"jsPsych.data.get().last({self.window})['trials'][0]['bean_{self.raw_name}']"


class FunctionVariable(Variable):
    """
    A variable that is the result of a function.
    Examples:
        >>> def add(a, b):
        ...     return a + b
        >>> FunctionVariable('a', add, [1, 2]).to_js()
        ((a,b) => {return a+b})(1, 2)

    """

    def __init__(self, name, fct, args):
        super().__init__(name)
        self.fct = fct
        self.args = args

    def to_js(self):
        fct_declaration = _fct_to_js(self.fct)
        fct_input = _fct_args_to_js(self.args)
        return f"({fct_declaration}){fct_input}"


class CodeVariable(Variable):
    """
    A variable to access JavaScript code.
    """

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def set(self):
        return f"let {self.name}={self.value};"

    def to_js(self):
        return self.name


class SharedVariable:
    """
    A variable that can be shared between different stimuli.
    """

    def __init__(self, name, value):
        self.name = str(name)
        self.value = value

    def set(self):
        return f"let {self.name}={self.value};"

    def to_js(self):
        return self.name


class SideEffect:
    def __init__(self, set_variable, get_variable):
        """
        A side effect that can set variables.
        """
        self.set_variable = set_variable
        self.get_variable = get_variable

    def to_js(self):
        return f"{self.set_variable.name}={self.get_variable.to_js()};"