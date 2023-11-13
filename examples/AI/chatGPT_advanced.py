import typing
import IPython

import openai

import funix


# @funix.new_funix_type(
#     {
#         "name": "textarea",
#         "config": {
#             "rows": 6,
#         },
#     }
# )
# class PromptBox(str):
#     pass


cfg = {  # declarative configuration, all in one place
    "description": """The ChatGPT app build in [Funix.io]""",
    "conditional_visible": [
        {"when": {"show_advanced_options": True}, "show": ["max_tokens"]}
    ],
    # "rate_limit": funix.decorator.Limiter.session(max_calls=2, period=60 * 60 * 24),
}


@funix.funix(**cfg)
def ChatGPT_advanced_stream(
    prompt: str,
    show_advanced_options: bool = True,
    max_tokens: range(100, 500, 50) = 150,
) -> IPython.display.Markdown:
    client = openai.OpenAI()  # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
        stream=True,
        max_tokens=max_tokens,
    )
    message = []
    for chunk in response:
        message.append(chunk.choices[0].delta.content or "")
        yield "".join(message)


@funix.funix(**cfg)
def ChatGPT_advanced(
    prompt: str,
    show_advanced_options: bool = True,
    max_tokens: range(100, 500, 50) = 150,
) -> IPython.display.Markdown:
    client = openai.OpenAI()  # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
        stream=False,
        max_tokens=max_tokens,
    )
    return response.choices[0].text
