
# from funix import import_theme, new_funix_type, funix
import funix 
# from funix.widget import slider
from funix.hint import StrTextarea, StrInputBox
# from typing import Literal
import typing 

import re


# @new_funix_type("slider", slider)
# class NewSlider(int):
#     pass


# inputBox = StrInputBox

funix.import_theme(
    {
        "name": "text",
        "widgets": {
            "bool": "switch",
            "Literal": "radio",
        },
    },
    alias="text",
)


@funix.funix(theme="text")
def replace_text(
    passage: funix.hint.StrTextarea,
    replace: str,
    replace_with: str,
    replace_all: bool = True,
    replace_styles: typing.Literal["Regex", "Native"] = "Native",
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
