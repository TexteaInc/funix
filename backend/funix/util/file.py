"""
File utils for funix.
"""

from atexit import register
from os import listdir
from os.path import abspath, exists, isdir, join, normpath, sep, splitext
from shutil import rmtree
from sys import path
from tempfile import mkdtemp
from typing import Any, Generator


def create_safe_tempdir() -> bytes | str:
    """
    Create a safe tempdir. It will be deleted when the program normally exits.

    Returns:
        bytes | str: See `tempfile.mkdtemp` for more info.
    """
    tempdir = mkdtemp()

    register(lambda: exists(tempdir) and rmtree(tempdir))

    return tempdir


def get_path_difference(base_path: str, target_path: str) -> str:
    """
    Get path difference from base dir and target_dir, and turn it to Python module like string.

    Parameters:
        base_path (str): The base directory.
        target_path (str): The target directory.

    Returns:
        str: The path difference.

    Raises:
        ValueError: If the base directory is not a prefix of the target directory.

    Examples / Doctest:
        >>> assert get_path_difference("/a/b", "/a/b/c/d") == "c.d"
        >>> assert get_path_difference("/abc", "/abc/de/c") == "de.c"
    """
    base_components = normpath(base_path).split(sep)
    target_components = normpath(target_path).split(sep)

    if not target_path.startswith(base_path):
        raise ValueError("The base directory is not a prefix of the target directory.")

    if len(base_components) == 1 and base_components[0] == ".":
        return ".".join(target_components)

    path_diff = target_components

    for _ in range(len(base_components)):
        path_diff.pop(0)

    return ".".join(path_diff)


def get_python_files_in_dir(
    base_dir: str,
    add_to_sys_path: bool,
    need_full_path: bool,
    is_dir: bool,
    matches: Any,
) -> Generator[str, None, None]:
    """
    Get all the Python files in a directory.

    Parameters:
        base_dir (str): The path.
        add_to_sys_path (bool): If the path should be added to sys.path.
        need_full_path (bool): If the full path is needed.
        is_dir (bool): If mode is dir mode.
        matches (Any): The matches.

    Returns:
        Generator[str, None, None]: The Python files.

    Notes:
        Need think a better way to get the Python files and think about the module.
    """
    if add_to_sys_path:
        path.append(base_dir)
    files = listdir(base_dir)
    for file in files:
        if isdir(join(base_dir, file)):
            yield from get_python_files_in_dir(
                join(base_dir, file), add_to_sys_path, need_full_path, is_dir, matches
            )
        if file.endswith(".py") and file != "__init__.py":
            full_path = join(base_dir, file)
            if matches:
                if matches(abspath(full_path)):
                    continue
            if need_full_path:
                yield join(base_dir, file)
            else:
                yield splitext(file)[0]
