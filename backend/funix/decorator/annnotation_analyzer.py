"""
For funix annotation analyzer.

Better version of magic, hope replace it in the future.
"""

from enum import Enum
from functools import wraps
from inspect import Parameter
from typing import Any, Callable

__registered__: dict[Parameter.annotation, Callable[[Parameter], dict]] = {}
"""
The registered annotation analyzers.

Key: The annotation.
Value: The analyzer function.
"""


def is_hashable(t):
    try:
        hash(t)
        return True
    except:  # No TypeError
        return False


class Step(Enum):
    """
    The step of the analyzer.
    """

    MAGIC = 0
    """
    The parsed data provided to the magic.
    """

    FRONTEND = 1
    """
    The parsed data provided to the frontend.
    """

    BOTH = 2
    """
    The parsed data provided to both the magic and the frontend.
    """


def register(annotation: Parameter.annotation, step: Step) -> callable:
    """
    Register an annotation analyzer.

    Parameters:
        annotation (Parameter.annotation): The annotation to register.
        step (Step): The step of the analyzer. Only for document.

    Returns:
        The decorator.
    """

    @wraps(register)
    def decorator(func: Callable[[Parameter], dict]) -> callable:
        """
        Decorator for register an annotation analyzer.

        Parameters:
            func (Callable[[Parameter, bool], dict]): The function.
        """
        __registered__[annotation] = func
        return func

    return decorator


def analyze(value: Parameter | Any) -> dict:
    """
    Analyze an annotation.

    Parameters:
        value (Parameter | Any): The value.

    Returns:
        dict: The analyzed result.
    """
    # check type un hashable
    if is_hashable(value):
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

    @register(ipywidgets.Password, Step.BOTH)
    def _ipywidgets(_: ipywidgets.Password) -> dict:
        return {"type": "string", "widget": "password"}


def register_pandera():
    """
    Register pandera type
    """
    from pandera import dtypes
    from pandera.engines import numpy_engine, pandas_engine

    @register(dtypes.Bool, Step.FRONTEND)
    @register(pandas_engine.BOOL, Step.FRONTEND)
    @register(numpy_engine.Bool, Step.FRONTEND)
    def _pandera_bool(_: Any) -> dict:
        return {"type": "boolean"}

    @register(dtypes.Float, Step.FRONTEND)
    @register(dtypes.Float16, Step.FRONTEND)
    @register(dtypes.Float32, Step.FRONTEND)
    @register(dtypes.Float64, Step.FRONTEND)
    @register(numpy_engine.Float16, Step.FRONTEND)
    @register(numpy_engine.Float32, Step.FRONTEND)
    @register(numpy_engine.Float64, Step.FRONTEND)
    def _pandera_float(_: Any) -> dict:
        return {"type": "number"}

    @register(dtypes.Int, Step.FRONTEND)
    @register(dtypes.Int8, Step.FRONTEND)
    @register(dtypes.Int16, Step.FRONTEND)
    @register(dtypes.Int32, Step.FRONTEND)
    @register(dtypes.Int64, Step.FRONTEND)
    @register(dtypes.UInt8, Step.FRONTEND)
    @register(dtypes.UInt16, Step.FRONTEND)
    @register(dtypes.UInt32, Step.FRONTEND)
    @register(dtypes.UInt64, Step.FRONTEND)
    @register(pandas_engine.INT8, Step.FRONTEND)
    @register(pandas_engine.INT16, Step.FRONTEND)
    @register(pandas_engine.INT32, Step.FRONTEND)
    @register(pandas_engine.INT64, Step.FRONTEND)
    @register(numpy_engine.Int8, Step.FRONTEND)
    @register(numpy_engine.Int16, Step.FRONTEND)
    @register(numpy_engine.Int32, Step.FRONTEND)
    @register(numpy_engine.Int64, Step.FRONTEND)
    @register(numpy_engine.UInt8, Step.FRONTEND)
    @register(numpy_engine.UInt16, Step.FRONTEND)
    @register(numpy_engine.UInt32, Step.FRONTEND)
    @register(numpy_engine.UInt64, Step.FRONTEND)
    def _pandera_float16(_: Any) -> dict:
        return {"type": "integer"}

    @register(dtypes.String, Step.FRONTEND)
    @register(pandas_engine.STRING, Step.FRONTEND)
    @register(pandas_engine.NpString, Step.FRONTEND)
    @register(numpy_engine.String, Step.FRONTEND)
    def _pandera_string(_: Any) -> dict:
        return {"type": "string"}
