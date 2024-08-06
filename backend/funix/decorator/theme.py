"""
Handle theme for decorator
"""
from typing import Optional

from funix.theme import get_dict_theme, parse_theme
from funix.util.uri import is_valid_uri

default_theme: dict = {}
"""
The default funix theme.
"""

themes = {}
"""
A dict, key is theme name, value is funix theme.
"""

parsed_themes = {}
"""
A dict, key is theme name, value is parsed MUI theme.
"""


def set_default_theme(theme: str) -> None:
    """
    Set the default theme.

    Parameters:
        theme (str): The theme alias, path or url.
    """
    global default_theme, parsed_themes, themes
    if theme in themes:
        theme_dict = themes[theme]
    else:
        if is_valid_uri(theme):
            theme_dict = get_dict_theme(None, theme)
        else:
            theme_dict = get_dict_theme(theme, None)
    default_theme = theme_dict
    parsed_themes["__default"] = parse_theme(default_theme)


def import_theme(
    source: str | dict,
    alias: Optional[str] = None,
) -> None:
    """
    Import a theme from path, url or dict.

    Parameters:
        source (str | dict): The path, url or dict of the theme.
        alias (str): The theme alias.

    Raises:
        ValueError: If the theme already exists.

    Notes:
        Check the `funix.theme.get_dict_theme` function for more information.
    """
    global themes
    if isinstance(source, str):
        if is_valid_uri(source):
            theme = get_dict_theme(None, source)
        else:
            theme = get_dict_theme(source, None)
    else:
        theme = source
    name = theme["name"]
    if alias is not None:
        name = alias
    if name in themes:
        raise ValueError(f"Theme {name} already exists")
    themes[name] = theme


def clear_default_theme() -> None:
    """
    Clear the default theme.
    """
    global default_theme, parsed_themes
    default_theme = {}
    parsed_themes.pop("__default")


def get_parsed_theme_fot_funix(theme: Optional[str] = None):
    """
    Get the parsed theme for funix.

    Parameters:
        theme (str): The theme name.

    Returns:
        The parsed theme for funix.
    """
    global parsed_themes
    if not theme:
        if "__default" in parsed_themes:
            return parsed_themes["__default"]
        else:
            return [], {}, {}, {}, {}
    else:
        if theme in parsed_themes:
            return parsed_themes[theme]
        else:
            # Cache
            if theme in themes:
                parsed_theme = parse_theme(themes[theme])
                parsed_themes[theme] = parsed_theme
            else:
                import_theme(theme, alias=theme)  # alias is not important here
                parsed_theme = parse_theme(themes[theme])
                parsed_themes[theme] = parsed_theme
            return parsed_theme
