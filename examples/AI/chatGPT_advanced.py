import os
import typing

import ipywidgets

import openai

openai.api_key = os.environ.get("OPENAI_KEY")

import funix


@funix.new_funix_type(
    {
        "name": "textarea",
        "config": {
            "rows": 6,
        },
    }
)
class PromptBox(str):
    pass


cfg = {  # declarative configuration, all in one place
    "description": """Try the **ChatGPT** app in [Funix](http://funix.io). **Note: An OpenAI key needs to be set in the environment variable OPENAI_KEY.""",
    "argument_labels": {
        "prompt": "_What do you wanna ask?_",
        "max_tokens": "**Length** of the answer",
        "show_advanced": "Show advanced options",
        "openai_key": "Use your own OpenAI key",
        "model": "Choose a model",
    },
    "widgets": {"openai_key": "password"},
    "conditional_visible": [
        {"when": {"show_advanced": True}, "show": ["max_tokens", "model", "openai_key"]}
    ],
}


@funix.funix(**cfg)
def ChatGPT_advanced(
    prompt: PromptBox,
    show_advanced: bool = False,
    model: typing.Literal["gpt-3.5-turbo", "gpt-3.5-turbo-0301"] = "gpt-3.5-turbo",
    max_tokens: range(100, 500, 50) = 150,
    openai_key: ipywidgets.Password = "use environment variable",
    # openai_key: str = "use environment variable",
) -> str:
    if openai_key != "use environment variable":
        openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]
