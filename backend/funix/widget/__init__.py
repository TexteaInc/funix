"""
This file contains the widget system for the funix project.
"""

from json import dumps
from typing import TypedDict

# Widget update
widgets_update_config = {}


def register_widget_update_config(widget: str) -> callable:
    """
    Register a widget update config function.
    You should register a function, that takes *args, and return a dict.
    The dict will be merged with the original config dict.
    This is used to update the config of a widget and solve the problem of the config of a widget is not complete.

    Parameters:
        widget(str): The name of the widget.

    Returns:
        The decorator.
    """

    def decorator(func: callable) -> None:
        """
        Decorator for register a widget update config function.

        Parameters:
            func(callable): The function.
        """
        widgets_update_config[widget] = func

    return decorator


def dump_frontend_config(widget_name: str, config: TypedDict) -> str:
    """
    Convert the config to a string that can be used in frontend. Will auto update the config if this widget has an
    update config function.

    Parameters:
        widget_name (str): The name of the widget.
        config (TypedDict): The config of the widget.

    Returns:
        str: The string that can be used in frontend.
    """
    flattened_config = list(config.values())
    if widget_name in widgets_update_config:
        update_function = widgets_update_config[widget_name]
        list_config = dumps(list(update_function(flattened_config).values()))
        return f"{widget_name}{list_config}"
    return f"{widget_name}{dumps(flattened_config)}"


class SliderConfig(TypedDict):
    """
    The config of the slider widget.
    """

    min: int | float
    """
    The minimum value of the slider.
    """
    max: int | float
    """
    The maximum value of the slider.
    """
    step: int | float
    """
    The step of the slider.
    """


@register_widget_update_config("slider")
def slider_config_update(*args) -> SliderConfig:
    """
    Update the config of the slider widget.

    Parameters:
        *args: The config of the slider widget.

    Returns:
        SliderConfig: The updated config of the slider widget.
    """
    new_config = SliderConfig(min=0, max=100, step=0.1)
    new_config.update(slider(*args[0])[1])
    return new_config


def slider(*args, **kwargs) -> (str, SliderConfig):
    """
    Create a slider widget config.

    Parameters:
        *args: The config of the slider widget. The order is `min`, `max`, `step`.
        **kwargs: The config of the slider widget. The key is `min`, `max`, `step`.

    Returns:
        (str, SliderConfig): The config of the slider widget.
            str: Widget name, always `slider`.
            SliderConfig: The config of the slider widget.
    """
    config = {"min": 0, "max": 100}
    if args:
        arg_names = ["min", "max", "step"]
        for i, arg in enumerate(args[: len(arg_names)]):
            config[arg_names[i]] = arg
    elif kwargs:
        config.update(kwargs)
    use_type = (
        int
        if all(
            isinstance(value, int)
            for value in [config["min"], config["max"], config.get("step")]
        )
        else float
    )
    if "step" not in config:
        config["step"] = 0.1 if use_type == float else 1
    config = SliderConfig(
        min=use_type(config["min"]),
        max=use_type(config["max"]),
        step=use_type(config["step"]),
    )
    return "slider", config


class CodeConfig(TypedDict):
    """
    The config of the code widget.
    """

    language: str
    """
    The language of the code.
    """


def code(language: str = "plaintext") -> (str, CodeConfig):
    """
    Create a code widget config.

    Parameters:
        language(str): The language of the code, default is `plaintext`.

    Returns:
        (str, CodeConfig): The config of the code widget.
            str: Widget name, always `code`.
            CodeConfig: The config of the code widget.
    """
    return "code", {"language": language}


def generate_frontend_widget_config(config: tuple[str, TypedDict] | str) -> str:
    """
    Generate the frontend widget config.

    Parameters:
        config((str, TypedDict) | str): The config of the widget.
            (str, TypedDict): Widget name and config, I will call `dump_frontend_config` to convert it to a str.
            str: Widget config (already in str), I will return it directly.
    """
    if isinstance(config, tuple):
        return dump_frontend_config(config[0], config[1])
    return config
