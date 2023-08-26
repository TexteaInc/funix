import os
import openai 
openai.api_key = os.environ.get("OPENAI_KEY")

messages  = []  # list of dicts, dict keys: role, content, system 

def print_messages_html(messages):
    printout = ""
    for message in messages:
        if message["role"] == "user":
            align, left, name = "left", "0%", "You"
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
    direction="column-reverse",
    # show_source=True 
)
def ChatGPT_multi_turn(current_message: str)  -> funix.hint.HTML:
    current_message = current_message.strip()
    messages.append({"role": "user", "content": current_message})
    completion = openai.ChatCompletion.create(
        messages=messages,
        model='gpt-3.5-turbo', 
        max_tokens=100,
    )
    chatgpt_response = completion["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": chatgpt_response})

    # return print_messages_markdown(messages)
    return print_messages_html(messages)
