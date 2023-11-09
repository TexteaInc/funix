from funix import funix
from funix.hint import Markdown
from funix.session import (
    get_global_variable,
    set_global_variable,
    set_default_global_variable,
)

from openai import OpenAI


set_default_global_variable("user_client", None)


@funix()
def set_openai_key(key: str) -> str:
    set_global_variable("user_client", OpenAI(api_key=key))
    return "Success"


@funix()
def simple_ask(prompt: str) -> Markdown:
    client: OpenAI | None = get_global_variable("user_client")
    if client is None:
        yield "Please set the OpenAI key first."
    else:
        stream = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            stream=True,
        )
        message = []
        for part in stream:
            message.append(part.choices[0].delta.content or "")
            yield "".join(message)
