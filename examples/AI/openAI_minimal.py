import os
import openai 
# openai.api_key = os.environ.get("OPENAI_KEY")

import typing 

import funix
from funix.session import get_global_variable, set_global_variable#, set_default_global_variable

# BUG: The set_global_variable() call does not effectively change the value of openai.api_key,
# though get_global_variable(openai.api_key) returns sessionized key value. 
# The value of openai.api_key remains None unless set via the environment variable OPENAI_KEY. 


@funix.funix( # Funix.io, the laziest way to build web apps in Python
  title="Set OpenAI key",
  argument_labels={
    "api_key": "Enter your API key", 
    "sys_env_var": "Use system environment variable"
  }, 
  conditional_visible=[ { "when": {"sys_env_var": False}, "show": ["api_key"],  } ],
    show_source=True
)
def set_openAI_key(api_key: str="", sys_env_var:bool=True) -> str:
    if sys_env_var:
        return "OpenAI API key is set in your environment variable. Nothing changes."
    else:
        if api_key == "":
            return "You entered an empty string. Try again."
        else:
            # openai.api_key = api_key 
            set_global_variable(openai.api_key, api_key)
            return "OpenAI API key has been set via the web form! If it was set via an environment variable before, it's now overwritten."

@funix.funix()
def get_openAI_key()->str:
    # return f"Your openAI key has been set to: {openai.api_key}" 
    return f"Your openAI key has been set to: {get_global_variable(openai.api_key)}" 


print (openai.api_key)

@funix.funix()
def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]

@funix.funix()
def dalle(Prompt: str) -> funix.hint.Image:
    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]


if __name__ == "__main__":
    from funix import run
    run(port=3000, main_class="ai")
    # TODO: how to call it in the latest version of Funix? 
