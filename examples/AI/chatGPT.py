import os  # Python's native


# import funix
# @funix.funix(
#     rate_limit=funix.decorator.Limiter.session(max_calls=2, period=60*60*24),
#     show_source=True
# )

# def ChatGPT_simplest(prompt: str) -> str:
#     completion = openai.ChatCompletion.create(
#         messages=[{"role": "user", "content": prompt}], model="gpt-3.5-turbo"
#     )
#     return completion["choices"][0]["message"]["content"]

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
import openai   
import IPython  # a famous library for interactive python

def ChatGPT(prompt: str) -> IPython.display.Markdown:
    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
        # stream=True,
    )
    return response.choices[0].message.content
    # message = []
    # for chunk in response:
    #     message.append(chunk.choices[0].delta.content or "")
    #     yield "".join(message)