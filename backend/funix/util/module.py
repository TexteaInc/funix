"""
Handle module
"""

from importlib.util import module_from_spec, spec_from_file_location
from inspect import getsourcefile, isclass, isfunction
from os.path import basename
from string import ascii_letters, digits
from types import ModuleType
from typing import Any, Optional
from uuid import uuid4

from funix import decorator, hint
from funix.app import app


def getsourcefile_safe(obj: Any) -> str | None:
    """
    Get the source file of the object.

    Note:
        Need think a better way to handle the class.

    Parameters:
        obj (Any): The object to get the source file.

    Returns:
        str: The source file.
        None: If the source file is not found, it may be a built-in object.
    """
    try:
        if isclass(obj):
            return getsourcefile(obj.__init__)
        return getsourcefile(obj)
    except:
        return None


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
    # safe_words = digits + ascii_letters + "_"
    # return "".join(
    #     map(
    #         lambda x: x
    #         if x in safe_words
    #         else "_"
    #         if x == "."
    #         else f"__Unicode_{ord(x)}__",
    #         name,
    #     )
    # )
    return name


def handle_module(
    module: Any,
    need_path: bool,
    base_dir: Optional[str],
    path_difference: Optional[str],
) -> None:
    """
    Import module's functions and classes to funix.
    It won't handle the object that is already handled by funix,
    or the object that is customized by the funix or private.

    Parameters:
        module (Any): The module to handle.
        need_path (bool): If the path is needed.
        base_dir (str | None): The base directory.
        path_difference (str | None): The path difference. See `funix.util.get_path_difference` for more info.
    """
    members = reversed(dir(module))
    for member in members:
        module_member = getattr(module, member)
        is_func = isfunction(module_member)
        is_cls = isclass(module_member)
        if is_func or is_cls:
            if getsourcefile_safe(module_member) != module.__file__:
                if hasattr(module_member, "__wrapped__"):
                    if getsourcefile_safe(module_member.__wrapped__) != module.__file__:
                        continue
                else:
                    continue
            in_funix = (
                decorator.object_is_handled(app, id(module_member))
                or id(module_member) in hint.custom_cls_ids
            )
            if in_funix:
                continue
            use_func = decorator.funix if is_func else decorator.funix_class
            if member.startswith("__") or member.startswith("_FUNIX_"):
                continue
            if need_path:
                if base_dir:
                    use_func(menu=path_difference)(module_member)
                else:
                    use_func(menu=f"{module.__name__}")(module_member)
            else:
                use_func()(module_member)
