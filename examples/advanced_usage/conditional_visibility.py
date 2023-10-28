import typing

import ipywidgets

import funix


@funix.funix(
    widgets={"prompt": "textarea"},
    conditional_visible=[
        {
            "when": {
                "show_advanced": True,
            },
            "show": ["max_tokens", "model", "openai_key"],
        }
    ],
)
def conditional_visible(
    prompt: str,
    show_advanced: bool = False,
    model: typing.Literal["gpt-3.5-turbo", "gpt-3.5-turbo-0301"] = "gpt-3.5-turbo",
    max_tokens: range(100, 200, 20) = 140,
    openai_key: ipywidgets.Password = "",
) -> str:
    return "This is a dummy function."
