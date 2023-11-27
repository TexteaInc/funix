import os  # Python's native

import openai   
import IPython  # a famous library for interactive python

# client = OpenAI()

# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )

# print(completion.choices[0].message)

import funix
@funix.funix(
    rate_limit=funix.decorator.Limiter.session(max_calls=2, period=60*60*24),
    show_source=True
)

def ChatGPT(prompt: str) -> IPython.display.Markdown:
    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def ChatGPT_stream(prompt: str) -> IPython.display.Markdown:
    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
        stream=True,
    )
    message = []
    for chunk in response:
        message.append(chunk.choices[0].delta.content or "")
        yield "".join(message)