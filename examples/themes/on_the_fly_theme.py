import typing

import funix


@funix.new_funix_type(
    widget={
        "name": "textarea",
        "config": {"minRows": 5, "maxRows": 8, "multiline": "True"}
        # This config is to be overwritten by the theme below
    }
)
class long_str(str):
    pass


theme = {
    "name": "my_new_theme",
    "widgets": {
        "long_str": ["textarea", {"minRows": 2, "maxRows": 4}],
        # "long_str": "textarea(minRows=2, maxRows=3)",
        # TODO: shall we support the function call syntax above?
        # Comment: Oh, here we go again
        "int": "slider(0, 10, 50)",
    },
}

funix.import_theme(theme, alias="my_new_theme")

funix.set_default_theme("my_new_theme")


@funix.funix(
    # theme="my_new_theme",  # This line not needed if set_default_theme above
)
def foo(x: long_str = "\n".join(map(str, range(8))), y: int = 40) -> str:
    return f"{x} {y}"
