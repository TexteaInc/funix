import json
from typing import TypedDict, Tuple


widget_config = Tuple[str, TypedDict]
def generate_widget_config(widget: str, config: TypedDict) -> widget_config:
    return widget, config

def generate_frontend_widget_config(config: widget_config | str) -> str:
    if isinstance(config, tuple):
        return f"{config[0]}{json.dumps(list(config[1].values()))}"
    return config

class slider_config(TypedDict):
    min: int | float
    max: int | float
    step: int | float


def slider(*args, **kwargs) -> Tuple[str, str]:
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
    use_type = float
    if "step" in config:
        use_type = int if isinstance(config["step"], int) and isinstance(config["min"], int) and isinstance(config["max"], int) else float
    else:
        use_type = int if isinstance(config["min"], int) and isinstance(config["max"], int) else float
        config["step"] = 1 if use_type is int else 0.1
    config = slider_config(min=use_type(config["min"]), max=use_type(config["max"]), step=use_type(config["step"]))
    return generate_widget_config("slider", config)
