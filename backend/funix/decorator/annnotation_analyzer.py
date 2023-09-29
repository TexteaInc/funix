"""
For funix annotation analyzer.

Better version of magic, hope replace it in the future.
"""

from typing import Callable, Any
from inspect import Parameter


__registered__: dict[Parameter.annotation, Callable[[Parameter], dict]] = {}
"""
The registered annotation analyzers.

Key: The annotation.
Value: The analyzer function.
"""


def register(annotation: Parameter.annotation) -> callable:
    """
    Register an annotation analyzer.

    Parameters:
        annotation (Parameter.annotation): The annotation to register.

    Returns:
        The decorator.
    """

    def decorator(func: Callable[[Parameter], dict]) -> None:
        """
        Decorator for register an annotation analyzer.

        Parameters:
            func (Callable[[Parameter, bool], dict]): The function.
        """
        __registered__[annotation] = func

    return decorator


def analyze(value: Parameter | Any) -> dict:
    """
    Analyze an annotation.

    Parameters:
        value (Parameter | Any): The value.

    Returns:
        dict: The analyzed result.
    """

    if isinstance(value, Parameter):
        annotation = value.annotation
        if annotation in __registered__:
            return __registered__[annotation](value)
    else:
        if value in __registered__:
            return __registered__[value](value)
    return {}


def register_ipywidgets():
    """
    Register ipywidgets.
    """
    import ipywidgets

    @register(ipywidgets.Password)
    def _ipywidgets(widget: ipywidgets.Password) -> dict:
        return {"type": "str", "widget": "password"}
