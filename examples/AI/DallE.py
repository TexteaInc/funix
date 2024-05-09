import os

import openai  # pip install openai

import IPython 

import funix 


cfg = {
    'title': 'OpenAI: Dall-E',
    'description': 'Generate an image with DALL-E in [Funix](http://funix.io), the minimalist way to build apps in Python. An OpenAI key needs to be set. A rate limit is applied. ',
    'rate_limit': funix.decorator.Limiter.session(max_calls=1, period=60*60*24), 'show_source': True}

@funix.funix(**cfg)
def dalle_create(
    Prompt: str = "a cat on a red jeep"
    ) -> IPython.display.Image:

    client = openai.OpenAI() # defaults to os.environ.get("OPENAI_API_KEY")

    response = client.images.generate(
        prompt=Prompt,
    )

    return response.data[0].url


# **Note:**
# * An OpenAI key needs to be set in the environment variable OPENAI_KEY.
# * A rate limit of 1 call per day per browser session is set.

# Like us? Please star us on [GitHub](https://github.com/TexteaInc/funix)].
