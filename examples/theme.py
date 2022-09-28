from pydatafront.decorator import import_theme, set_global_theme, textea_export

import_theme("http://127.0.0.1:8000/sunset_v2.yaml", "sunset")
set_global_theme("sunset")


@textea_export(
    path="theme_test",
    description="Sunset: [config](https://yazawazi.moe/pdf_themes/sunset_v2.yaml)",
    int_input={
        "treat_as": "config"
    },
    float_input={
        "treat_as": "config"
    },
    bool_input={
        "treat_as": "config"
    },
    str_input={
        "treat_as": "config"
    }
)
def theme_test(int_input: int, float_input: float, bool_input: bool, str_input: str):
    return {
        "int": int_input,
        "float": float_input,
        "bools": bool_input,
        "str": str_input
    }
