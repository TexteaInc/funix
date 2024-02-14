from funix.app import app
from funix.config.switch import GlobalSwitchOption
from funix.hint import DecoratedFunctionListItem

default_function: str | None = None
"""
Default function id.
"""

default_function_name: str | None = None
"""
Default function name.
"""

cached_list_functions: list[dict] = []
"""
Cached list functions. For `/list` route.
"""

module_functions_counter: dict[str, int] = {}
"""
A dict, key is module name, value is the number of functions in the module.
"""

decorated_functions_list: list[DecoratedFunctionListItem] = []
"""
A list, each element is a dict, record the information of the decorated function.

See `DecoratedFunctionListItem` for more information.
"""


def set_default_function_name(name: str) -> None:
    """
    Set this function as default.
    """
    global default_function_name
    default_function_name = name


def set_default_function(_id: str) -> None:
    """
    Set this function as default.
    """
    global default_function
    default_function = _id


def make_decorated_functions_happy() -> list[dict]:
    """
    Make the decorated functions happy

    Cache the list of functions, and remove the module if there is only one function in the module.
    """
    global cached_list_functions, decorated_functions_list
    if not GlobalSwitchOption.DISABLE_FUNCTION_LIST_CACHE:
        if cached_list_functions:
            return cached_list_functions
    new_decorated_functions_list = []
    for i in decorated_functions_list:
        if i["module"] in module_functions_counter:
            if module_functions_counter[i["module"]] == 1:
                if "." in i["module"]:
                    i["module"] = ".".join(i["module"].split(".")[0:-1])
                else:
                    i["module"] = None
        new_decorated_functions_list.append(i)
    if not GlobalSwitchOption.DISABLE_FUNCTION_LIST_CACHE:
        cached_list_functions = new_decorated_functions_list
    return new_decorated_functions_list


def is_empty_function_list() -> bool:
    """
    Check if the function list is empty.

    Returns:
        bool: True if empty, False otherwise.
    """
    global decorated_functions_list
    return len(decorated_functions_list) == 0


def push_counter(module: str) -> None:
    """
    Push the module counter.

    Parameters:
        module (str): The module name.
    """
    global module_functions_counter
    if module in module_functions_counter:
        module_functions_counter[module] += 1
    else:
        module_functions_counter[module] = 1


def get_default_function_name() -> str | None:
    """
    Get the default function name.

    Returns:
        str | None: The default function name.
    """
    global default_function_name
    return default_function_name


def decorated_functions_list_append(item: dict) -> None:
    """
    Append a decorated function to the list.

    Parameters:
        item (dict): The decorated function.
    """
    global decorated_functions_list
    decorated_functions_list.append(item)


def enable_list():
    global cached_list_functions, default_function

    @app.get("/list")
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
            "list": make_decorated_functions_happy(),
            "default_function": default_function,
        }
