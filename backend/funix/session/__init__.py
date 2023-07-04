"""
Control the global variables.
"""

from copy import deepcopy
from typing import Any

from flask import session

UserID = str
"""
User ID, `__funix_id` in session.
"""

VariableName = str
"""
Global variable name.
"""

VariableValue = Any
"""
Global variable value.
"""

__funix_global_variables: dict[UserID, dict[VariableName, VariableValue]] = {}
"""
Funix global variables.

Record the global variables of each user.
"""

__funix_default_global_variables: dict[VariableName, VariableValue] = {}
"""
Funix default global variables.

Record the default global variables.
"""


def set_global_variable(name: str, value: Any) -> None:
    """
    Set the global variable.

    Parameters:
        name (str): The global variable name.
        value (Any): The global variable value.

    Raises:
        RuntimeError: If the user id is not found in session.
    """
    global __funix_global_variables
    user_id = session.get("__funix_id")
    if not user_id:
        raise RuntimeError("User ID not found in session.")
    if user_id not in __funix_global_variables:
        __funix_global_variables[user_id] = {}
    __funix_global_variables[user_id][name] = value


def set_default_global_variable(name: str, value: Any) -> None:
    """
    Set the default global variable.

    Parameters:
        name (str): The global variable name.
        value (Any): The global variable value.
    """
    global __funix_default_global_variables
    __funix_default_global_variables[name] = value


def get_global_variable(name: str) -> Any:
    """
    Get the global variable.

    Parameters:
        name (str): The global variable name.

    Returns:
        Any: The global variable value.

    Raises:
        RuntimeError: If the user id is not found in session.
    """
    global __funix_global_variables, __funix_default_global_variables
    user_id = session.get("__funix_id")
    if not user_id:
        raise RuntimeError("User ID not found in session.")
    if user_id not in __funix_global_variables:
        __funix_global_variables[user_id] = {}
    if name not in __funix_global_variables[user_id]:
        __funix_global_variables[user_id][name] = deepcopy(
            __funix_default_global_variables.get(name, None)
        )
    return __funix_global_variables[user_id].get(name, None)
