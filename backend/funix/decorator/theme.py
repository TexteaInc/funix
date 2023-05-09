import atexit
import copy
import os
import shutil
import tempfile
from typing import Any, Optional
from uuid import uuid4 as uuid
import importlib.util

import requests

__theme_style_sugar_dict = {
    "fontColor": {
        "root": {
            "color": "${value}"
        }
    }
}
__basic_widgets = ["slider", "input", "textField", "switch", "button", "checkbox", "radio"]


def dict_replace(original_dict: dict, original: str, new: Any):
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


def get_full_style_from_sugar(key: str, value: Any):
    sugar_info = __theme_style_sugar_dict[key]
    return dict_replace(sugar_info, "${value}", value)


def get_mui_theme(theme, colors, typography):
    mui_theme = {
        "components": {},
        "palette": {},
        "typography": {},
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
            "styleOverrides": {}
        }
        for prop_name in theme[widget_name].keys():
            if prop_name == "style":
                mui_theme["components"][widget_mui_name]["styleOverrides"].update(theme[widget_name][prop_name])
            elif prop_name == "color":
                color_name = f"temp_{uuid().hex}"
                if not theme[widget_name][prop_name] in mui_theme["palette"]:
                    if theme[widget_name][prop_name] in temp_colors.keys():
                        mui_theme["components"][widget_mui_name]["defaultProps"][prop_name] = \
                            temp_colors[theme[widget_name][prop_name]]
                    else:
                        mui_theme["palette"][color_name] = {"main": theme[widget_name][prop_name]}
                        mui_theme["components"][widget_mui_name]["defaultProps"][prop_name] = color_name
                        temp_colors[theme[widget_name][prop_name]] = color_name
                true_color = mui_theme["palette"][color_name]["main"]
                style_override = {}
                if widget_name == "input":
                    style_override = {
                        "underline": {
                            "&:before": {
                                "borderColor": true_color
                            },
                            "&&:hover::before": {
                                "borderColor": true_color
                            }
                        }
                    }
                if widget_name == "textField":
                    style_override = {
                        "root": {
                            "& fieldset": {
                                "borderColor": true_color
                            },
                            "&&:hover fieldset": {
                                "border": "2px solid",  # Hmmm
                                "borderColor": true_color
                            }
                        }
                    }
                if style_override != {}:
                    mui_theme["components"][widget_mui_name]["styleOverrides"].update(style_override)
            elif prop_name in __theme_style_sugar_dict.keys():
                mui_theme["components"][widget_mui_name]["styleOverrides"].update(
                    get_full_style_from_sugar(prop_name, theme[widget_name][prop_name])
                )
            else:
                mui_theme["components"][widget_mui_name]["defaultProps"][prop_name] = theme[widget_name][prop_name]
    return mui_theme


def parse_theme(theme):
    type_names = []
    type_widget_dict = {}
    widget_style = {}
    custom_palette = {}
    custom_typography = {}
    if "widgets" in theme:
        for type_name in theme["widgets"]:
            if isinstance(type_name, tuple):
                for name in type_name:
                    type_names.append(name)
                    type_widget_dict[name] = theme["widgets"][type_name]
            else:
                type_names.append(type_name)
                type_widget_dict[type_name] = theme["widgets"][type_name]
    if "palette" in theme:
        for color_name in theme["palette"].keys():
            custom_palette[color_name] = theme["palette"][color_name]
    if "props" in theme:
        if "basic" in theme["props"]:
            if "color" in theme["props"]["basic"]:
                if "primary" in custom_palette:
                    custom_palette["primary"]["main"] = theme["props"]["basic"]["color"]
                else:
                    custom_palette["primary"] = {"main": theme["props"]["basic"]["color"]}
                del theme["props"]["basic"]["color"]
            if "contrastText" in theme["props"]["basic"]:
                if "primary" in custom_palette:
                    custom_palette["primary"]["contrastText"] = theme["props"]["basic"]["contrastText"]
                else:
                    custom_palette["primary"] = {"contrastText": theme["props"]["basic"]["contrastText"]}
                del theme["props"]["basic"]["contrastText"]
            for basic_widget_name in __basic_widgets:
                widget_style[basic_widget_name] = copy.deepcopy(theme["props"]["basic"])
            del theme["props"]["basic"]
        for widget_name in theme["props"].keys():
            if widget_name in widget_style:
                widget_style[widget_name].update(theme["props"][widget_name])
            else:
                widget_style[widget_name] = theme["props"][widget_name]
    if "typography" in theme:
        custom_typography = theme["typography"]
    mui_theme = get_mui_theme(widget_style, custom_palette, custom_typography)
    return type_names, type_widget_dict, widget_style, custom_palette, mui_theme


def get_dict_theme(
    path: Optional[str] = None,
    url: Optional[str] = None,
    module: Optional[dict] = None,
    dict_name: Optional[str] = None
) -> dict:
    # check args
    if dict_name is None:
        if module is None:
            raise ValueError("Module must be specified when dict_name is not specified, "
                             "if you specify path or url, must specify dict_name!")
    else:
        if path is None and url is None:
            raise ValueError("Must specify path or url when dict_name is specified!")
        elif path is not None and url is not None:
            raise ValueError("Can't specify both path and url!")

    # import theme
    name = uuid().hex
    if path:
        sepc = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(sepc)
        sepc.loader.exec_module(module)
    elif url:
        tempdir = tempfile.mkdtemp()

        @atexit.register
        def remove_temp():
            shutil.rmtree(tempdir)

        py_theme_path = os.path.join(tempdir, name + ".py")

        with open(py_theme_path, "wb") as f:
            f.write(requests.get(url).content)

        sepc = importlib.util.spec_from_file_location(name, py_theme_path)
        module = importlib.util.module_from_spec(sepc)
        sepc.loader.exec_module(module)
    elif module is not None:
        return module
    theme = getattr(module, dict_name)
    return theme
