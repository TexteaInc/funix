from typing import Callable, Type

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

uuid_with_name: dict[str, dict[str, str]] = {}
"""
A dict, key is the app name, value is a dict, key is the UUID, value is the function name.
"""

function_id_with_uuid: dict[str, dict[int, str]] = {}
"""
A dict, key is the app name, value is a dict, key is the function id, value is the UUID.
"""

class_method_map: dict[str, dict[str, tuple[Callable | None, Callable | None]]] = {}
"""
{app_name: {method_qualname: (org_method, funix_method)}}
"""

class_map: dict[str, dict[str, Type]] = {}
"""
{app_name: {class_name: class}}
"""


def set_class(app_name: str, class_name: str, class_: Type) -> None:
    """
    Set the class.

    Parameters:
        app_name (str): The app name.
        class_name (str): The class name.
        class_ (Type): The class.
    """
    global class_map
    if app_name in class_map:
        class_map[app_name][class_name] = class_
    else:
        class_map[app_name] = {class_name: class_}


def get_class(app_name: str, class_name: str) -> Type | None:
    """
    Get the class.

    Parameters:
        app_name (str): The app name.
        class_name (str): The class name.

    Returns:
        Type | None: The class.
    """
    global class_map
    return class_map.get(app_name, {}).get(class_name, None)


def set_class_method_org(
    app_name: str, method_qualname: str, org_method: Callable
) -> None:
    """
    Set the original method of the class method.

    Parameters:
        app_name (str): The app name.
        method_qualname (str): The method qualname.
        org_method (Callable): The original method.
    """
    global class_method_map
    if app_name in class_method_map:
        if method_qualname in class_method_map[app_name]:
            class_method_map[app_name][method_qualname] = (
                org_method,
                class_method_map[app_name][method_qualname][1],
            )
        else:
            class_method_map[app_name][method_qualname] = (org_method, None)
    else:
        class_method_map[app_name] = {method_qualname: (org_method, None)}


def set_class_method_funix(
    app_name: str, method_qualname: str, funix_method: Callable
) -> None:
    """
    Set the funix method of the class method.

    Parameters:
        app_name (str): The app name.
        method_qualname (str): The method qualname.
        funix_method (Callable): The funix method.
    """
    global class_method_map
    if app_name in class_method_map:
        if method_qualname in class_method_map[app_name]:
            class_method_map[app_name][method_qualname] = (
                class_method_map[app_name][method_qualname][0],
                funix_method,
            )
        else:
            class_method_map[app_name][method_qualname] = (None, funix_method)
    else:
        class_method_map[app_name] = {method_qualname: (None, funix_method)}


def get_class_method_org(app_name: str, method_qualname: str) -> Callable | None:
    """
    Get the original method of the class method.

    Parameters:
        app_name (str): The app name.
        method_qualname (str): The method qualname.

    Returns:
        Callable | None: The original method.
    """
    global class_method_map
    return class_method_map.get(app_name, {}).get(method_qualname, (None, None))[0]


def get_class_method_funix(app_name: str, method_qualname: str) -> Callable | None:
    """
    Get the funix method of the class method.

    Parameters:
        app_name (str): The app name.
        method_qualname (str): The method qualname.

    Returns:
        Callable | None: The funix method.
    """
    global class_method_map
    return class_method_map.get(app_name, {}).get(method_qualname, (None, None))[1]


def get_function_uuid_with_id(app_name: str, _id: int) -> str:
    """
    Get the UUID by the function id.

    Parameters:
        app_name (str): The app name.
        _id (int): The function id.

    Returns:
        str: The UUID.
    """
    global function_id_with_uuid
    return function_id_with_uuid.get(app_name, {}).get(_id, "")


def set_function_uuid_with_id(app_name: str, _id: int, uuid: str) -> None:
    """
    Set the UUID with the function id.

    Parameters:
        app_name (str): The app name.
        _id (int): The function id.
        uuid (str): The UUID.
    """
    global function_id_with_uuid
    if app_name in function_id_with_uuid:
        function_id_with_uuid[app_name][_id] = uuid
    else:
        function_id_with_uuid[app_name] = {_id: uuid}


def get_function_detail_by_uuid(app_name: str, uuid: str) -> dict:
    """
    Get the function detail by the function id.

    Parameters:
        app_name (str): The app name.
        uuid (srt): The function UUID.

    Returns:
        dict: The function detail.
    """
    global decorated_functions_list
    for i in decorated_functions_list.get(app_name, []):
        if i["id"] == uuid:
            return i
    return {}


def set_uuid_with_name(app_name: str, _id: str, name: str) -> None:
    """
    Set the UUID with the name.

    Parameters:
        app_name (str): The app name.
        _id (str): The UUID.
        name (str): The function name.
    """
    global uuid_with_name
    if app_name in uuid_with_name:
        uuid_with_name[app_name][_id] = name
    else:
        uuid_with_name[app_name] = {_id: name}


def get_uuid_with_name(app_name: str, _id: str) -> str:
    """
    Get the function name by UUID.

    Parameters:
        app_name (str): The app name.
        _id (str): The UUID.

    Returns:
        str: The function name.
    """
    global uuid_with_name
    return uuid_with_name.get(app_name, {}).get(_id, "Unknown")


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
