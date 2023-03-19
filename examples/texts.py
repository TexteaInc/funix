from funix import set_theme, new_funix_type, funix
from funix.widget import slider
from funix.widget.builtin import StrTextarea, StrInputBox
from typing import Literal

import re

@new_funix_type("slider", slider)
class NewSlider(int):
    pass

inputbox = StrInputBox


set_theme({
    "name": "text",
    "widgets": {
        "bool": "switch",
        "Literal": "radio"
    }
})



@funix(
    theme="text"
)
def replace_text(
    passage: StrTextarea,
    replace: inputbox,
    replace_with: inputbox,
    replace_all: bool = True,
    replace_styles: Literal["Regex", "Native"] = "Native"
) -> str:
    if replace_styles == "Regex":
        if replace_all:
            return re.sub(replace, replace_with, passage)
        else:
            return re.sub(replace, replace_with, passage, 1)
    elif replace_styles == "Native":
        if replace_all:
            return passage.replace(replace, replace_with)
        else:
            return passage.replace(replace, replace_with, 1)
    else:
        return "Ahh ohh, something went wrong."
