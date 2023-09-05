# Building a one-turn chatbot from any causal language model hosted on HuggingFace using free Inference API

# Copyleft 2023 Forrest Sheng Bao http://forrestbao.github.io 
# The purpose of this code is to demonstrate the use of Funix to turn a simple API call function to a web app. 

# To turn this code into a web app, run the following command in the terminal:
# funix huggingface.py -l # the -l flag is very important. It tells Funix to load the function as a web app.

import os, json, typing # Python's native 
import requests # pip install requests

API_TOKEN = os.getenv("HF_TOKEN") # "Please set your API token as an environment variable named HF_TOKEN. You can get your token from https://huggingface.co/settings/token"

def huggingface(
    model_name: typing.Literal[
        "gpt2", 
        "bigcode/starcoder", 
        "google/flan-t5-base"] = "gpt2", 
    prompt: str = "Who is Einstein?") -> str: 

    payload = {"inputs": prompt} # not all models use this query  and output formats.  Hence, we limit the models above. 

    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.post(API_URL, headers=headers, json=payload)

    if "error" in response.json(): 
        return response.json()["error"]
    else:
        return response.json()[0]["generated_text"]