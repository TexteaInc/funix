"""
File utils for funix.
"""

from shutil import rmtree
from os.path import exists
from atexit import register
from tempfile import mkdtemp


def create_safe_tempdir() -> bytes | str:
    """
    Create a safe tempdir. It will be deleted when the program normally exits.

    Returns:
        bytes | str: See `tempfile.mkdtemp` for more info.
    """
    tempdir = mkdtemp()

    register(lambda: exists(tempdir) and rmtree(tempdir))

    return tempdir

