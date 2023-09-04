# Turn this function to a web app using the command: 
# funix chatGPT_lazy.py -l # -l flag must be there. 


import os # Python's native 
import openai  # you cannot skip it 

openai.api_key = os.environ.get("OPENAI_KEY")

def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]
