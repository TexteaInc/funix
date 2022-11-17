from funix.decorator import import_theme, set_global_theme, funix_export

import_theme("./sunset_v2.yaml", "sunset")
set_global_theme("sunset")


@funix_export(
    path="theme_test",
    description="Sunset: [config](https://yazawazi.moe/pdf_themes/sunset_v2.yaml)"
)
def theme_test(int_input: int, float_input: float, bool_input: bool, str_input: str):
    return {
        "int": int_input,
        "float": float_input,
        "bools": bool_input,
        "str": str_input
    }
