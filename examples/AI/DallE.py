import os 

import openai  # pip install openai
openai.api_key = os.environ.get("OPENAI_KEY")

import IPython.display

import funix 

@funix.funix(  # Funix.io, the laziest way to build web apps in Python
    title="OpenAI: Dall-E",
    description="""Generate an image by prompt with DALL-E.""",
    widgets={"openai_key": "password"},
    show_source=True,
)
def dalle(
    Prompt: str = "a cat on a red jeep",
    openai_key: str = "using environment variable",
) -> IPython.display.Image:
    if openai_key != "using environment variable":
        openai.api_key = openai_key

    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]