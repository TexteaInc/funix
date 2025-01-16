"""
This file contains some shared config for debug and production.
It's a global switch for quick turning on/off some key features in Funix.
"""

from secrets import token_hex
from sys import modules
from typing import Union


class SwitchOption:
    """Switch option."""

    AUTO_CONVERT_UNDERSCORE_TO_SPACE_IN_NAME: bool = True
    """Auto convert underscore to space in name"""

    DISABLE_FUNCTION_LIST_CACHE: bool = False
    """No cache for function list"""

    AUTO_READ_DOCSTRING_TO_FUNCTION_DESCRIPTION: bool = True
    """Auto read docstring to function description"""

    AUTO_READ_DOCSTRING_TO_PARSE: bool = True
    """Auto parse docstring to function widgets and description"""

    DOCSTRING_TO_ARGUMENT_HELP: bool = True
    """Auto parse docstring to function argument help"""

    DOCSTRING_FIRST_LINE_TO_TITLE: bool = False
    """Auto parse docstring first line to function title"""

    USE_FIXED_SESSION_KEY: Union[bool, str] = False
    """Use fixed session key"""

    FILE_LINK_EXPIRE_TIME: int = 60 * 60
    """The file link expire time (seconds), -1 for never expire"""

    BIGGER_DATA_SAVE_TO_TEMP: int = 1024 * 1024 * 10
    """The bigger data size to save to temp (bytes), -1 for always in memory"""

    NOTEBOOK_AUTO_EXECUTION: bool = False
    """In notebook, auto run the flask app"""

    __session_key = None

    @property
    def in_notebook(self) -> bool:
        """Whether in notebook."""
        return "ipykernel" in modules and self.NOTEBOOK_AUTO_EXECUTION

    def get_session_key(self) -> str:
        """Get the session key."""
        if self.__session_key is not None:
            return self.__session_key

        if isinstance(self.USE_FIXED_SESSION_KEY, str):
            self.__session_key = self.USE_FIXED_SESSION_KEY
            return self.USE_FIXED_SESSION_KEY

        self.__session_key = token_hex(16)
        return self.__session_key


GlobalSwitchOption = SwitchOption()
