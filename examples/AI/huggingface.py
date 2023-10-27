# Building a one-turn chatbot from any causal language model hosted on HuggingFace using free Inference API

# Copyleft 2023 Forrest Sheng Bao http://forrestbao.github.io 
# The purpose of this code is to demonstrate the use of Funix to turn a simple API call function to a web app. 

# To turn this code into a web app, run the following command in the terminal:
# funix huggingface.py -l # the -l flag is very important. It tells Funix to load the function as a web app.

import os, json, typing # Python's native 
import requests # pip install requests
import ipywidgets

# API_TOKEN = os.getenv("HF_TOKEN") # "Please set your API token as an environment variable named HF_TOKEN. You can get your token from https://huggingface.co/settings/token"

import funix

@funix.funix(
    description="""Talk to LLMs hosted at HuggingFace. A HuggingFace token needs to be set in the environment variable HF_TOKEN.""",
    # rate_limit=funix.decorator.Limiter.session(max_calls=20, time_frame=60*60*24),
)
def huggingface(
    model_name: typing.Literal[
        "gpt2", 
        "bigcode/starcoder", 
        "google/flan-t5-base"] = "gpt2", 
    prompt: str = "Who is Einstein?", 
    API_TOKEN: ipywidgets.Password = None
    ) -> str: 

    payload = {"inputs": prompt, "max_tokens":200} # not all models use this query  and output formats.  Hence, we limit the models above. 

    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {API_TOKEN.value}"}

    response = requests.post(API_URL, headers=headers, json=payload)

    if "error" in response.json(): 
        return response.json()["error"]
    else:
        return response.json()[0]["generated_text"]