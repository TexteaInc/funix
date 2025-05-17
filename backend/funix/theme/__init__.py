"""
For parsing theme.
"""

import json
from copy import deepcopy
from os.path import join
from typing import Optional, Union
from uuid import uuid4

from requests import get

from funix.config import basic_widgets
from funix.util.file import create_safe_tempdir
from funix.widget import dump_frontend_config

__theme_style_sugar_dict = {"fontColor": {"root": {"color": "${value}"}}}
"""
Syntactic sugar replacement dictionary.

We only support `fontColor` now.
"""


def dict_replace(original_dict: dict, original: str, new: any) -> dict:
    """
    Dictionary replacement tool, recursively replace all values that match the original value.

    Parameters:
        original_dict (dict): The original dictionary.
        original (str): The original value.
        new (any): The new value.

    Returns:
        dict: The new dictionary.
    """
    if isinstance(original_dict, dict):
        return {
            key: dict_replace(value, original, new)
            for key, value in original_dict.items()
        }

    # str
    if original_dict == original:
        return new
    else:
        return original_dict


def get_full_style_from_sugar(key: str, value: any) -> dict:
    """
    Syntactic sugar replacement
    Replace the ${value} in the key with value.

    Parameters:
        key (str): The key.
        value (any): The value.

    Returns:
        dict: The full style.
    """
    sugar_info = __theme_style_sugar_dict[key]
    return dict_replace(sugar_info, "${value}", value)


def get_mui_theme(
    theme: dict,
    colors: dict,
    typography: dict,
    overrides: dict,
    funix_options: dict,
) -> dict:
    """
    Generate MUI theme from widget style, palette and typography.
    Again, there are no detailed type annotations, please read the Funix documentation and the TS types for MUI Theme.

    Parameters:
        theme (dict): The theme.
        colors (dict): The colors.
        typography (dict): The typography.
        overrides (dict): The overrides.
        funix_options (dict): The funix options.

    Returns:
        dict: The MUI theme.
    """
    mui_theme = {
        "components": {},
        "palette": {},
        "typography": {},
        # funix only
        "funix_header": "{{org}}",
        "funix_footer": "{{org}}",
        "funix_run_button": "Run",
        "funix_disable_footer_icons": False,
        "funix_disable_input_title": True,
        "funix_grid_height": 450,
        "funix_grid_checkbox": True,
        "funix_autorun_label": "Auto-run",
    }
    temp_colors = {}
    if colors:
        for color in colors.keys():
            if color in ["mode", "divider", "contrastThreshold", "tonalOffset"]:
                mui_theme["palette"][color] = colors[color]
            elif isinstance(colors[color], str):
                mui_theme["palette"][color] = {"main": colors[color]}
            else:
                mui_theme["palette"][color] = colors[color]
    if typography:
        mui_theme["typography"] = typography
    for widget_name in theme.keys():
        widget_mui_name = "Mui" + widget_name[0].upper() + widget_name[1::]
        mui_theme["components"][widget_mui_name] = {
            "defaultProps": {},
            "styleOverrides": {},
        }
        for prop_name in theme[widget_name].keys():
            if prop_name == "style":
                mui_theme["components"][widget_mui_name]["styleOverrides"].update(
                    theme[widget_name][prop_name]
                )
            elif prop_name == "color":
                color_name = f"temp_{uuid4().hex}"
                if not theme[widget_name][prop_name] in mui_theme["palette"]:
                    if theme[widget_name][prop_name] in temp_colors.keys():
                        mui_theme["components"][widget_mui_name]["defaultProps"][
                            prop_name
                        ] = temp_colors[theme[widget_name][prop_name]]
                    else:
                        mui_theme["palette"][color_name] = {
                            "main": theme[widget_name][prop_name]
                        }
                        mui_theme["components"][widget_mui_name]["defaultProps"][
                            prop_name
                        ] = color_name
                        temp_colors[theme[widget_name][prop_name]] = color_name
                true_color = mui_theme["palette"][color_name]["main"]
                style_override = {}
                if widget_name == "input":
                    style_override = {
                        "underline": {
                            "&:before": {"borderColor": true_color},
                            "&&:hover::before": {"borderColor": true_color},
                        }
                    }
                if widget_name == "textField":
                    style_override = {
                        "root": {
                            "& fieldset": {"borderColor": true_color},
                            "&&:hover fieldset": {
                                "border": "2px solid",  # Hmmm
                                "borderColor": true_color,
                            },
                        }
                    }
                if style_override != {}:
                    mui_theme["components"][widget_mui_name]["styleOverrides"].update(
                        style_override
                    )
            elif prop_name in __theme_style_sugar_dict.keys():
                mui_theme["components"][widget_mui_name]["styleOverrides"].update(
                    get_full_style_from_sugar(prop_name, theme[widget_name][prop_name])
                )
            else:
                mui_theme["components"][widget_mui_name]["defaultProps"][prop_name] = (
                    theme[widget_name][prop_name]
                )
    if overrides:
        mui_theme["components"].update(overrides)
    if funix_options:
        funix_options_add_funix_prefix = {
            "funix_" + key: funix_options[key] for key in funix_options.keys()
        }
        mui_theme.update(funix_options_add_funix_prefix)
    return mui_theme


def parse_theme(theme: dict) -> tuple[list[str], dict, dict, dict, dict]:
    """
    Parse the funix types theme into a mui theme and other useful data.
    Due to the complexity of theme, we do not provide type annotations for theme for now.
    But you can still go to the documentation and read about the theme definition.

    Parameters:
        theme (dict): The funix theme to parse.

    Returns:
        (list[str], dict, dict, dict, dict): A tuple containing the following:
            list[str], index 0: types that in the theme
            dict, index 1: dict of type as key, widget as value, representing the relationship between type and widget
            dict, index 2: widget style
            dict, index 3: custom palette
            dict, index 4: mui theme, for funix to use
    """
    type_names = []
    type_widget_dict = {}
    widget_style = {}
    custom_palette = {}
    custom_typography = {}
    raw_overrides = {}
    funix_options = {}

    if "widgets" in theme:
        # for type_name in theme["widgets"]:
        #     list_type_name = (
        #         list(type_name) if isinstance(type_name, tuple) else [type_name]
        #     )
        #     for name in list_type_name:
        #         type_names.append(name)
        #         type_widget_dict[name] = theme["widgets"][type_name]

        # Oh, here we go again
        # for type_widget_group in theme["widgets"]:
        #     data_types = type_widget_group["data_type"]
        #     widget_type = type_widget_group["widget_type"]
        #     if isinstance(widget_type, list):
        #         widget_type = dump_frontend_config(widget_type[0], widget_type[1])
        #     list_data_types = (
        #         data_types if isinstance(data_types, list) else [data_types]
        #     )
        #     for data_type in list_data_types:
        #         type_names.append(data_type)
        #         type_widget_dict[data_type] = widget_type

        for type_name in theme["widgets"]:
            widget = theme["widgets"][type_name]
            if isinstance(widget, list):
                widget = dump_frontend_config(widget[0], widget[1])
            if isinstance(widget, dict):
                widget_name = widget["widget"]
                widget_config: Union[None, dict] = widget.get("props", None)
                if widget_name.startswith("@"):
                    pass
                else:
                    if widget_config is None:
                        widget = widget_name
                    else:
                        widget = dump_frontend_config(widget_name, widget_config)
            type_names.append(type_name)
            type_widget_dict[type_name] = widget
    if "palette" in theme:
        for color_name in theme["palette"].keys():
            custom_palette[color_name] = theme["palette"][color_name]
    if "props" in theme:
        if "basic_widgets" in theme["props"]:
            # INFO: Remove temporarily
            # if "color" in theme["props"]["basic_widgets"]:
            #     if "primary" in custom_palette:
            #         custom_palette["primary"]["main"] = theme["props"]["basic_widgets"]["color"]
            #     else:
            #         custom_palette["primary"] = {
            #             "main": theme["props"]["basic_widgets"]["color"]
            #         }
            #     del theme["props"]["basic_widgets"]["color"]
            # if "contrastText" in theme["props"]["basic_widgets"]:
            #     if "primary" in custom_palette:
            #         custom_palette["primary"]["contrastText"] = theme["props"]["basic_widgets"][
            #             "contrastText"
            #         ]
            #     else:
            #         custom_palette["primary"] = {
            #             "contrastText": theme["props"]["basic_widgets"]["contrastText"]
            #         }
            #     del theme["props"]["basic_widgets"]["contrastText"]
            for basic_widget_name in basic_widgets:
                widget_style[basic_widget_name] = deepcopy(
                    theme["props"]["basic_widgets"]
                )
            del theme["props"]["basic"]
        for widget_name in theme["props"].keys():
            # list_widget_name = (
            #     list(widget_name) if isinstance(widget_name, tuple) else [widget_name]
            # )
            # for name in list_widget_name:
            #     if name in widget_style:
            #         widget_style[name].update(theme["props"][widget_name])
            #     else:
            #         widget_style[name] = theme["props"][widget_name]
            if widget_name in widget_style:
                widget_style[widget_name].update(theme["props"][widget_name])
            else:
                widget_style[widget_name] = theme["props"][widget_name]
    if "typography" in theme:
        custom_typography = theme["typography"]
    if "overrides" in theme:
        raw_overrides = theme["overrides"]

    if "funix" in theme:
        funix_options = theme["funix"]

    mui_theme = get_mui_theme(
        widget_style, custom_palette, custom_typography, raw_overrides, funix_options
    )
    return type_names, type_widget_dict, widget_style, custom_palette, mui_theme


def get_dict_theme(
    path: Optional[str] = None,
    url: Optional[str] = None,
) -> dict:
    """
    Get the funix theme from a path, url.

    Parameters:
        path (str, optional): The path of the theme file.
        url (str, optional): The url of the theme file.

    Returns:
        dict: The funix theme.

    Raises:
        ValueError: See the doc of the function.
    """
    if path:
        return json.loads(open(path, "r").read())
        # module = import_module_from_file(path, False)
    elif url:
        name = uuid4().hex
        tempdir = create_safe_tempdir()

        py_theme_path = join(tempdir, name + ".py")

        with open(py_theme_path, "wb") as f:
            f.write(get(url).content)

        return json.loads(open(py_theme_path, "r").read())
    else:
        raise ValueError("Oops, something went wrong!")
