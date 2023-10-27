import os 

import openai  # pip install openai
openai.api_key = os.environ.get("OPENAI_KEY")

import IPython.display

import funix 

@funix.funix(  # Funix.io, the laziest way to build web apps in Python
    title="OpenAI: Dall-E",
    description="""Generate an image by prompt with DALL-E. **Note:** An OpenAI key needs to be set in the environment variable OPENAI_KEY.""",
    show_source=True,
)
def dalle(
    Prompt: str = "a cat on a red jeep"
) -> IPython.display.Image:

    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]