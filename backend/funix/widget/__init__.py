import json
from typing import TypedDict


def generate_widget_config(widget: str, config: TypedDict) -> tuple[str, TypedDict]:
    return widget, config


widgets_update_config = {}


def register_widget_update_config(widget: str):
    def decorator(func):
        widgets_update_config[widget] = func

    return decorator


def dump_frontend_config(config: tuple[str, TypedDict]) -> str:
    if config[0] in widgets_update_config:
        list_config = json.dumps(list(widgets_update_config[config[0]](list(config[1].values())).values()))
        return f"{config[0]}{list_config}"
    return f"{config[0]}{json.dumps(list(config[1].values()))}"


class SliderConfig(TypedDict):
    min: int | float
    max: int | float
    step: int | float


@register_widget_update_config("slider")
def slider_config_update(*args) -> SliderConfig:
    new_config = SliderConfig(min=0, max=100, step=0.1)
    new_config.update(slider(*args[0])[1])
    return new_config


def slider(*args, **kwargs) -> tuple[str, TypedDict]:
    config = {
        "min": 0,
        "max": 100
    }
    if args:
        if len(args) == 1:
            config["max"] = args[0]
        elif len(args) == 2:
            config["min"], config["max"] = args[0], args[1]
        elif len(args) == 3:
            config["min"], config["max"], config["step"] = args[0], args[1], args[2]
    elif kwargs:
        if "max" in kwargs:
            config["max"] = kwargs["max"]
            if "min" in kwargs:
                config["min"] = kwargs["min"]
            if "step" in kwargs:
                config["step"] = kwargs["step"]
    if "step" in config:
        use_type = int if isinstance(config["step"], int) and isinstance(config["min"], int) and isinstance(
            config["max"], int) else float
    else:
        use_type = int if isinstance(config["min"], int) and isinstance(config["max"], int) else float
    if "step" not in config:
        config["step"] = 0.1 if use_type == float else 1
    config = SliderConfig(min=use_type(config["min"]), max=use_type(config["max"]), step=use_type(config["step"]))
    return generate_widget_config("slider", config)


def code(language: str) -> tuple[str, TypedDict]:
    return generate_widget_config("code", {"language": language})


def generate_frontend_widget_config(config: tuple[str, TypedDict] | str) -> str:
    if isinstance(config, tuple):
        return dump_frontend_config(config)
    return config
