from flask import Flask

from funix.config.switch import GlobalSwitchOption
from funix.hint import DecoratedFunctionListItem

default_function: dict[str, str | None] = {}
"""
Default function id.
"""

default_function_name: dict[str, str | None] = {}
"""
Default function name.
"""

cached_list_functions: dict[str, list[dict]] = {}
"""
Cached list functions. For `/list` route.
"""

module_functions_counter: dict[str, dict[str, int]] = {}
"""
A dict, key is module name, value is the number of functions in the module.
"""

decorated_functions_list: dict[str, list[DecoratedFunctionListItem]] = {}
"""
A list, each element is a dict, record the information of the decorated function.

See `DecoratedFunctionListItem` for more information.
"""


def set_default_function_name(app_name: str, name: str) -> None:
    """
    Set this function as default.

    Parameters:
        app_name (str): The app name.
        name (str): The function name.
    """
    global default_function_name
    default_function_name[app_name] = name


def set_default_function(app_name: str, _id: str) -> None:
    """
    Set this function as default.

    Parameters:
        app_name (str): The app name.
        _id (str): The function id.
    """
    global default_function
    default_function[app_name] = _id


def make_decorated_functions_happy(app_name: str) -> list[dict]:
    """
    Make the decorated functions happy

    Cache the list of functions, and remove the module if there is only one function in the module.

    Parameters:
        app_name (str): The app name.
    """
    global cached_list_functions, decorated_functions_list
    if not GlobalSwitchOption.DISABLE_FUNCTION_LIST_CACHE:
        if app_name in cached_list_functions and cached_list_functions[app_name]:
            return cached_list_functions[app_name]
    new_decorated_functions_list = []
    if app_name not in decorated_functions_list:
        decorated_functions_list[app_name] = []

    for i in decorated_functions_list[app_name]:
        if app_name in module_functions_counter:
            if i["module"] in module_functions_counter[app_name]:
                if module_functions_counter[app_name][i["module"]] == 1:
                    if "." in i["module"]:
                        i["module"] = ".".join(i["module"].split(".")[0:-1])
                    else:
                        i["module"] = None
            new_decorated_functions_list.append(i)
    if not GlobalSwitchOption.DISABLE_FUNCTION_LIST_CACHE:
        cached_list_functions[app_name] = new_decorated_functions_list
    return new_decorated_functions_list


def is_empty_function_list(app_name: str) -> bool:
    """
    Check if the function list is empty.

    Returns:
        bool: True if empty, False otherwise.

    Parameters:
        app_name (str): The app name.
    """
    global decorated_functions_list
    if app_name not in decorated_functions_list:
        return True
    return len(decorated_functions_list[app_name]) == 0


def push_counter(app_name: str, module: str) -> None:
    """
    Push the module counter.

    Parameters:
        app_name (str): The app name.
        module (str): The module name.
    """
    global module_functions_counter
    if app_name in module_functions_counter:
        if module in module_functions_counter[app_name]:
            module_functions_counter[app_name][module] += 1
        else:
            module_functions_counter[app_name][module] = 1
    else:
        module_functions_counter[app_name] = {module: 1}


def get_default_function_name(app_name: str) -> str | None:
    """
    Get the default function name.

    Parameters:
        app_name (str): The app name.

    Returns:
        str | None: The default function name.
    """
    global default_function_name
    if app_name in default_function_name:
        return default_function_name.get(app_name, None)
    else:
        return None


def decorated_functions_list_append(app_name: str, item: dict) -> None:
    """
    Append a decorated function to the list.

    Parameters:
        app_name (str): The app name.
        item (dict): The decorated function.
    """
    global decorated_functions_list
    if app_name in decorated_functions_list:
        decorated_functions_list[app_name].append(item)
    else:
        decorated_functions_list[app_name] = [item]


def enable_list(flask_app: Flask):
    global cached_list_functions, default_function

    @flask_app.get("/list")
    def __funix_export_func_list() -> dict:
        """
        Send the full function list.

        Routes:
            /list: The list path, we don't consider the GET "/" route, because it is the index page. And we start
                   frontend and backend at the same port.

        Returns:
            dict: The function list.
        """
        return {
            "list": make_decorated_functions_happy(flask_app.name),
            "default_function": default_function.get(flask_app.name, None),
        }
