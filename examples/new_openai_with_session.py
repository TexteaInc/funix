from funix import funix
from IPython.display import Markdown

from openai import OpenAI

user_client = None

@funix()
def set_openai_key(key: str) -> str:
    global user_client
    user_client = OpenAI(api_key=key)
    return "Success"


@funix()
def chatGPT(prompt: str) -> Markdown:
    client: None | OpenAI = user_client
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
