import copy
from typing import Any
from uuid import uuid4 as uuid


__theme_style_sugar_dict = {
    "fontColor": {
        "root": {
            "color": "${value}"
        }
    }
}
__basic_widgets = ["slider", "input", "textField", "switch", "button", "checkbox"]

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
            if color == "mode":
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
                styleOverride = {}
                if widget_name == "input":
                    styleOverride = {
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
                    styleOverride = {
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
                if styleOverride != {}:
                    mui_theme["components"][widget_mui_name]["styleOverrides"].update(styleOverride)
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
    if "styles" in theme:
        if "basic" in theme["styles"]:
            if "color" in theme["styles"]["basic"]:
                if "primary" in custom_palette:
                    custom_palette["primary"]["main"] = theme["styles"]["basic"]["color"]
                else:
                    custom_palette["primary"] = {"main": theme["styles"]["basic"]["color"]}
                del theme["styles"]["basic"]["color"]
            if "contrastText" in theme["styles"]["basic"]:
                if "primary" in custom_palette:
                    custom_palette["primary"]["contrastText"] = theme["styles"]["basic"]["contrastText"]
                else:
                    custom_palette["primary"] = {"contrastText": theme["styles"]["basic"]["contrastText"]}
                del theme["styles"]["basic"]["contrastText"]
            for basic_widget_name in __basic_widgets:
                widget_style[basic_widget_name] = copy.deepcopy(theme["styles"]["basic"])
            del theme["styles"]["basic"]
        for widget_name in theme["styles"].keys():
            if widget_name in widget_style:
                widget_style[widget_name].update(theme["styles"][widget_name])
            else:
                widget_style[widget_name] = theme["styles"][widget_name]
    if "colors" in theme:
        for color_name in theme["colors"].keys():
            custom_palette[color_name] = theme["colors"][color_name]
    if "typography" in theme:
        custom_typography = theme["typography"]
    mui_theme = get_mui_theme(widget_style, custom_palette, custom_typography)
    return type_names, type_widget_dict, widget_style, custom_palette, mui_theme
