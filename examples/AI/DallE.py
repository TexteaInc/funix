import os

import openai  # pip install openai

openai.api_key = os.environ.get("OPENAI_KEY")

import funix 


@funix.funix(  # Funix.io, the laziest way to build web apps in Python
    title="OpenAI: Dall-E",
    description="""Generate an image with DALL-E in [Funix](http://funix.io), the minimalist way to build apps in Python. An OpenAI key needs to be set. A rate limit is applied. """,
    rate_limit=funix.decorator.Limiter.session(max_calls=1, period=60 * 60 * 24),
    show_source=True,
)
def dalle(
    Prompt: str = "a cat on a red jeep",
    openai_key: str = "using environment variable",
) -> funix.hint.Image:
    if openai_key != "using environment variable":
        openai.api_key = openai_key

    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]


# **Note:**
# * An OpenAI key needs to be set in the environment variable OPENAI_KEY.
# * A rate limit of 1 call per day per browser session is set.

# Like us? Please star us on [GitHub](https://github.com/TexteaInc/funix)].
