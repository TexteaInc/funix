from funix.decorator import import_theme, set_global_theme, funix

import_theme("./sunset_v2.yaml", "sunset")
set_global_theme("sunset")


@funix(
    path="theme_test",
    description="Sunset, the theme file is in the examples folder",
)
def theme_test(int_input: int, float_input: float, bool_input: bool, str_input: str):
    return {
        "int": int_input,
        "float": float_input,
        "bools": bool_input,
        "str": str_input
    }
