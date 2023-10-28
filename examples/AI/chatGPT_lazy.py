import os  # Python's native
import openai  # you cannot skip it

openai.api_key = os.environ.get("OPENAI_KEY")

import funix
@funix.funix(
    rate_limit=funix.decorator.Limiter.session(max_calls=2, time_frame=60*60*24),
    show_source=True
)

# If in lazy model, the decorator lines above should be commented out. 
# Lazy model means run this command
# $ funix -l chatGPT_lazy.py


def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}], model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]
