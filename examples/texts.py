from funix import import_theme, new_funix_type, funix
from funix.widget import slider
from funix.hint import StrTextarea, StrInputBox
from typing import Literal

import re


@new_funix_type("slider", slider)
class NewSlider(int):
    pass


inputBox = StrInputBox

import_theme(alias="text", module={
    "name": "text",
    "widgets": {
        "bool": "switch",
        "Literal": "radio"
    }
})


@funix(
    theme_name="text"
)
def replace_text(
    passage: StrTextarea,
    replace: inputBox,
    replace_with: inputBox,
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
