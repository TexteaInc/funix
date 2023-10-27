"""
Handle module
"""

from importlib.util import module_from_spec, spec_from_file_location
from os.path import basename
from string import ascii_letters, digits
from types import ModuleType
from uuid import uuid4


def import_module_from_file(path: str, need_name: bool) -> ModuleType:
    """
    Import module from file. Like the name.

    Parameters:
        path (str): The path to the file.
        need_name (bool): If the name of the module is also important, so set it to True, I hope this will work.

    Returns:
        types.ModuleType: The module.
    """
    if need_name:
        name = basename(path).replace(".py", "")
    else:
        name = uuid4().hex
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def funix_menu_to_safe_function_name(name: str) -> str:
    """
    Convert the funix menu name to a safe function name.

    Parameters:
        name (str): The funix menu name.

    Returns:
        str: The safe function name.
    """
    safe_words = digits + ascii_letters + "_"
    return "".join(
        map(
            lambda x: x
            if x in safe_words
            else "_"
            if x == "."
            else f"__Unicode_{ord(x)}__",
            name,
        )
    )
