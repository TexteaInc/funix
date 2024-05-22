import typing
import IPython

import openai

import funix

cfg = {
    "conditional_visible": [
        {"when": {"show_advanced_options": True}, "show": ["model", "max_tokens", "stream"]}
    ],
    # "rate_limit": funix.decorator.Limiter.session(max_calls=2, period=60 * 60 * 24),
}


@funix.funix(**cfg)
def ChatGPT_advanced_stream(
    prompt: str,
    show_advanced_options: bool = False,
    stream: bool = True,
    model: typing.Literal["gpt-3.5-turbo", "gpt-4"] = "gpt-3.5-turbo",
    max_tokens: range(100, 500, 50) = 150
) -> IPython.display.Markdown:
    """
    The ChatGPT app built in [Funix.io](http://funix.io)
    """
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
