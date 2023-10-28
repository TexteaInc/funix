import os, json
import typing

import requests
import IPython
import ipywidgets

import openai

import funix
from funix.session import get_global_variable, set_global_variable

# openai.api_key = os.environ.get("OPENAI_KEY")
# openai_key = os.environ.get("OPENAI_KEY")
openai_key = ""


# @funix.funix(  # Funix.io, the laziest way to build web apps in Python
#     title="Set OpenAI key",
#     argument_labels={
#         "api_key": "Enter your API key",
#         "use_sys_env_var": "Use system environment variable",
#     },
#     conditional_visible=[
#         {
#             "when": {"use_sys_env_var": False},
#             "show": ["api_key"],
#         }
#     ],
#     show_source=True,
# )
# def set_openAI_key(api_key: str = "") -> str:
#     if api_key == "":
#         return "You entered an empty string. Try again."
#     else:
#         global openai_key
#         openai_key = api_key
#         return f"Your openAI key has been set to: {openai_key}"

#         # openai.api_key = api_key
#         # set_global_variable(openai.api_key, api_key)
#         # FIXME: The two lines above are both useless to change openai.api_key. That's why we have to use POST method below to query all OpenAI endpoints. This is something to be fixed after grand opening.
#         return "OpenAI API key has been set via the web form! If it was set via an environment variable before, it's now overwritten."


# @funix.funix()
# def get_openAI_key() -> str:
#     return f"Your openAI key has been set to: {openai_key}"


@funix.funix()
def ChatGPT_POST(
    openai_key: ipywidgets.Password, 
    prompt: str="What is the meaning of life?", ) -> str:
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key.value}",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"{prompt}"}],
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=header, json=payload
    )

    if "error" in response.json(): 
        return response.json()["error"]["message"]
    else:
        return response.json()["choices"][0]["message"]["content"]


# @funix.funix()
def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}], model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]


@funix.funix()
def dalle_POST(
    openai_key: ipywidgets.Password, 
    prompt: str="a flying cat in a red pajama") -> (str, IPython.display.Image):
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key.value}",
    }
    payload = {"prompt": f"{prompt}"}
    response = requests.post(
        "https://api.openai.com/v1/images/generations", headers=header, json=payload
    )
    if "error" in response.json(): 
        return response.json()["error"]["message"] + "\n A place holder image below", "https://picsum.photos/200/300" 
    else:
        return "here is your picture", response.json()["data"][0]["url"]


# @funix.funix()
def dalle(Prompt: str) -> IPython.display.Image:
    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]


if __name__ == "__main__":
    from funix import run

    run(port=3000, file_or_module_name=__file__)
