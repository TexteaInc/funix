import os
import typing

import ipywidgets

import openai

# openai.api_key = os.environ.get("OPENAI_KEY")
# Disable this app from being called in public hosted examples

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
    "description": """Try the **ChatGPT** app in [Funix](http://funix.io), the minimalist way to build apps in Python. """,
    "argument_labels": {
        "prompt": "_What do you wanna ask?_",
        "max_tokens": "**Length** of the answer",
    },
    "conditional_visible": [
        {"when": {"show_advanced_options": True}, "show": ["max_tokens", "model"]}
    ],
    "rate_limit": funix.decorator.Limiter.session(max_calls=2, period=60 * 60 * 24),
}


@funix.funix(**cfg)
def ChatGPT_advanced(
    prompt: PromptBox,
    show_advanced_options: bool = True,
    model: typing.Literal["gpt-3.5-turbo", "gpt-3.5-turbo-0613"] = "gpt-3.5-turbo",
    max_tokens: range(100, 500, 50) = 150,
    # openai_key: ipywidgets.Password = "use environment variable",
) -> str:
    # if openai_key != "use environment variable":
    #     openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]
