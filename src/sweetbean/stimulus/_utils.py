from typing import List, Union

from sweetbean.parameter import DerivedParameter, TimelineVariable

StringType = Union[None, str, DerivedParameter, TimelineVariable]
IntType = Union[None, int, TimelineVariable, DerivedParameter]
FloatType = Union[None, float, TimelineVariable, DerivedParameter]
StringTypeL = Union[List[StringType], StringType]
IntTypeL = Union[List[IntType], IntType]


def add_warning(test):
    """Decorator to mark flagged values for an attribute."""

    def decorator(func):
        func.test_language = test  # Attach flagged values to the function
        return func

    return decorator
