"""
Handle module
"""

from importlib.util import module_from_spec, spec_from_file_location
from os.path import basename
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
