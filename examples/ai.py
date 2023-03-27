import os
import openai 
openai.api_key = os.environ.get("OPENAI_KEY")

import typing 

import funix

@funix.funix()
def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]

@funix.funix(
        description="""Try the **ChatGPT** app in [Funix](http://funix.io)""",
        argument_labels = {
            "prompt" : "_What do you wanna ask?_",
            "max_tokens": "**Length** of the answer",
            "show_advanced": "Show advanced options",
            "openai_key": "Use your own OpenAI key",
            "model": "Choose a model",
        },
        widgets={"openai_key": "password", "model": "radio",
                 "show_advanced": "checkbox", "show_verbose": "switch"},
        conditional_visible=[
            {"if": {"show_advanced": True,}, 
             "then": ["max_tokens", "model", "openai_key"]}
        ],
        show_source=True 
)
def ChatGPT_advanced(prompt: str, 
            show_advanced: bool = False,
            model : typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0301']= 'gpt-3.5-turbo',
            max_tokens: range(20, 100, 20)=80,
            openai_key: str = "",)  -> str:      
    if openai_key != "":     
        openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model, 
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]

## ChatGPT multi-turn
messages  = []  # list of dicts, dict keys: role, content

def print_messages_html(messages):
    printout = ""
    for message in messages:
        if message["role"] == "user":
            align, left, name = "left", "1%", "You"
        elif message["role"] == "assistant":
            align, left, name = "right", "30%", "ChatGPT"
        printout += f'<div style="position: relative; left: {left}; width: 70%"><b>{name}</b>: {message["content"]}</div>'
    return printout

def print_messages_markdown(messages):
    printout = ""
    for message in messages:
        if message["role"] == "user":
            mark, name =  "**", "You"
        elif message["role"] == "assistant":
            mark, name =  "_", "ChatGPT"
        line = message["content"].strip().replace("\n", " ")
        printout += f'{mark}{name}: {line}{mark}\n'
        if message["role"] == "assistant":
            printout += "\n"
    return printout

import funix 
@funix.funix(
    show_source=True 
)
def ChatGPT_multi_turn(current_message: str)  -> funix.hint.HTML:
    current_message = current_message.strip()
    messages.append({"role": "user", "content": current_message})
    completion = openai.ChatCompletion.create(
        messages=messages,
        model='gpt-3.5-turbo', 
        max_tokens=40,
    )
    chatgpt_response = completion["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": chatgpt_response})

    # return print_messages_markdown(messages)
    return print_messages_html(messages)

@funix.funix( # Funix.io, the laziest way to build web apps in Python
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


@funix.funix()
def dalle(Prompt: str) -> funix.hint.Image:
    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]

# a professor with a laptop on an flying elephant
    # title="Dall-E",
    # description="""Generate an image by prompt with DALL-E""",
    # show_source=True


if __name__ == "__main__":
    from funix import run
    run(port=3000, main_class="ai")
