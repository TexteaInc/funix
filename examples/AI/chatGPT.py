import os  # Python's native

import openai   
import IPython  # a famous library for interactive python

def ChatGPT(prompt: str="Who is Cauchy?") -> IPython.display.Markdown:
    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def ChatGPT_stream(prompt: str="Who is Cauchy?") -> IPython.display.Markdown:
    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
        stream=True,
    )
    message = []
    for chunk in response: # streaming from OpenAI
        message.append(chunk.choices[0].delta.content or "")
        yield "".join(message)
