import os
import IPython     
from openai import OpenAI
import funix

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

messages  = []  # list of dicts, dict keys: role, content, system

@funix.funix(
    disable=True,
)
def print_messages_html(messages):
    printout = ""
    for message in messages:
        if message["role"] == "user":
            align, name = "left", "You"
        elif message["role"] == "assistant":
            align, name = "right", "ChatGPT"
        printout += f'<div style="width: 100%; text-align: {align}"><b>{name}</b>: {message["content"]}</div>'
    return printout


@funix.funix(
    direction="column-reverse",
)
def ChatGPT_multi_turn(current_message: str)  -> IPython.display.HTML:
    current_message = current_message.strip()
    messages.append({"role": "user", "content": current_message})
    completion = client.chat.completions.create(messages=messages,
    model='gpt-3.5-turbo',
    max_tokens=100)
    chatgpt_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": chatgpt_response})

    # return print_messages_markdown(messages)
    return print_messages_html(messages)
