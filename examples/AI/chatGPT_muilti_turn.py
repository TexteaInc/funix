import os
import openai

client = openai.OpenAI()

import IPython

messages = []  # list of dicts, dict keys: role, content, system

def print_messages_html(messages):
    printout = ""
    for message in messages:
        if message["role"] == "user":
            align, left, name = "left", "0%", "You"
        elif message["role"] == "assistant":
            align, left, name = "right", "30%", "ChatGPT"
        printout += f'<div style="position: relative; left: {left}; width: 70%"><b>{name}</b>: {message["content"]}</div>'
    return printout

import funix

cfg = {
    "rate_limit": funix.decorator.Limiter.session(max_calls=3, period=60 * 60 * 24),
    "direction": "column-reverse",  # input is below log
}

@funix.funix(**cfg)
def ChatGPT_multi_turn(current_message: str="Tell me a joke about Python the programming language.") -> IPython.display.HTML:
    global messages # every user has his/her own chat session with ChatGPT
    current_message = current_message.strip()
    messages.append({"role": "user", "content": current_message})
    completion = client.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    chatgpt_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": chatgpt_response})

    return print_messages_html(messages)
