from funix import set_theme, set_default_theme, funix
from themes.sunset import sunset
import typing

set_theme(sunset)
set_default_theme("sunset")


@funix(
    description="Widgets in the sunset theme. Theme file, sunset_v2.yaml is in the same directory as this script.",
    widgets={'int_input_inputbox': 'inputbox',
             'bool_input_switch': 'switch',
             'literal_input_radio': 'radio'}
)
def theme_test(
    int_input: int,
    float_input: float,
    int_input_inputbox: int,
    bool_input: bool,
    bool_input_switch: bool,
    literal_input_radio: typing.Literal["a", "b", "c"],
    str_input: str) :
    return {
        "int": int_input,
        "float": float_input,
        "bools": bool_input,
        "str": str_input
    }
