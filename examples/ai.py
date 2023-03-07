import os

import openai 
openai.api_key = os.environ.get("OPENAI_KEY")

from funix import funix 

@funix(
        title = "ChatGPT app in only two additional lines",
        argument_labels = {
            "prompt" : "What do you wanna ask?",
            "max_tokens": "Length of the answer"
        },
        widgets = {
            "prompt": "password"
        },
        theme = "https://github.com/TexteaInc/funix/blob/main/examples/sunset_v2.yaml"
)
def ChatGPT(prompt: str, 
            max_tokens: int)-> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt}],
        max_tokens = max_tokens
    )
    return completion["choices"][0]["message"]["content"]








@funix( # Funix.io, the laziest way to build web apps in Python
  title="Set OpenAI key",
  argument_labels={
    "api_key": "Enter your API key", 
    "sys_env_var": "Use system environment variable"
  }, 
  conditional_visible=[ { "if": {"sys_env_var": False}, "then": ["api_key"],  } ],
    show_source=True
)
def set(api_key: str="", sys_env_var:bool=True) -> str:
    if sys_env_var:
        return "OpenAI API key is set in your environment variable. Nothing changes."
    else:
        if api_key == "":
            return "You entered an empty string. Try again."
        else:
            openai.api_key = api_key
            return "OpenAI API key has been set via the web form! If it was set via an environment variable, it's been overwritten."

from funix.hint import Image
@funix( # Funix.io, the laziest way to build web apps in Python
    title="Dall-E",
    description="""
Generate an image by prompt with DALL-E

You need to set your OpenAI API key first. To do so, click on the "Set OpenAI key" button above. Then come back here by clicking on the "Dall-E" button again.""",
    show_source=True
)
def dalle(Prompt: str = "a cat on a red jeep") -> Image:
    response = openai.Image.create(prompt=Prompt, n=1, size="1024x1024")
    return response["data"][0]["url"]

if __name__ == "__main__":
    from funix import run
    run(port=3000, main_class="ai")
