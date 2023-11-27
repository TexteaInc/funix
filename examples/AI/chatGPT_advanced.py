import typing
import IPython

import openai

import funix


# @funix.new_funix_type(
#     {
#         "name": "radio"
#     }
# )
# class RadioRange(range):
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
    model: typing.Literal["gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613"] = "gpt-3.5-turbo",
    stream: bool = True,
    max_tokens: range(100, 500, 50) = 150
) -> IPython.display.Markdown:
    client = openai.OpenAI()  # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        stream=stream,
        max_tokens=max_tokens
    )
    if stream: 
        message = []
        for chunk in response:
            message.append(chunk.choices[0].delta.content or "")
            yield "".join(message)
    else: # no stream 
        yield response.choices[0].message.content
