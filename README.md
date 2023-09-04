<h1 align="center">
    <b>
        Funix.IO<br>
    </b>
    ⭐️  The laziest way to build AI/data apps in Python.  ⭐️ <br>
</h1>


<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

<h4><a href="https://youtu.be/DVIV_EUFNbw">Intro video</a> | <a href="https://github.com/TexteaInc/funix-doc/blob/main/Reference.md">Reference Manual</a> | <a href="https://github.com/TexteaInc/funix/edit/main/README.md#gallery"> Gallery </a> </h4>

https://user-images.githubusercontent.com/438579/236646521-30ed67f4-4708-4cf1-858d-33b65bc53b6a.mp4

</div>

## Features

Funix is designed for a data/ML engineer to build apps without writing UI-related code, not even selecting a widget, passing it to a Python function or link it to a call-back function. UI-related stuff should be left to a style file designed by the UI team. 

* **Minimalist**: Automatic UI generation. No manual widget selection.
* **Centralized styling**: Type-to-widget mapping stored in themes for cross-app UI consistency. 
* **Declarative**: All controls done via JSON strings. 
* **Non-intrusive**: You can still run or debug your Python code locally as usual.

Funix fully supports common built-in data types of Python, and major scientific types such as `matplotlib`'s `Figure` or `Jaxtyping`. 

The widgets are built on top of popular UI frameworks such as Material UI, and exposes major `props` for users to configure without knowing React or JavaScript.

You can further bring your function-turned app to the cloud via  [Funix-Deploy](https://github.com/TexteaInc/funix-deploy). 

## Hello, world! 

Building a web app in Funix is super easy. Just have a type-hinted Python function: 

```python
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Save in a file (say `hello.py`) and pass to Funix:

```bash
funix -l hello.py
```

A web app will be launched at `http://localhost:3000` and automatically opened in a browser window like below: 

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)

> **Note**: The `-l` flag stands for _"lazy"_ meaning that only default settings are used. It cannot be used when your function is decorated by the funix decorator `@funix()` which allows you to customize your app. For more details, please refer to the [reference manual]([docs/Reference.md](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md)).


## Zen: The types become widgets automatically

The Zen of Funix is to choose widgets for function I/Os based on their types, instead of picking a widget for each I/O. In this sense, **Funix to Python is like CSS to HTML or a `.sty` file to LaTeX**. Ideally, a Data Scientist or a Machine Learning Engineer should NOT touch anything UI -- s/he should leave all that to the UI team. 

The manual widget creating approach that other frameworks are redundant and inefficient. The same function I/O needs to appear twice: once in the function's signature, and the other time in the widget creation code. If you modify the interface of the function, you have to modify the widget creation code as well. 

The example below shows how different Python's built-in data types are mapped to different widgets. 

```python
import typing 

import funix

def my_chatbot(
    prompt: str, 
    advanced_features: bool = False,
    model: typing.Literal[
        'GPT-3.5', 'GPT-4.0', 
        'Llama-2', 'Falcon-7B']= 'GPT-4.0',
    max_token: range(100, 200, 20)=140,
    )  -> str:      
    pass
```

![four input types](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/input_widgets.png)

You can define your own types and associate widgets to them. For example, the `str` type is mapped to a single-line text input box where the text is displayed as you type by default. But you can create a new type for passwords which are replaced with asterisks. Thus, you can do something like this (coming soon!): 

```python 
import funix

@funix.new_funix_type(
    widget=[
        "@mui/material/TextField", # the component in MUI
        {"type":"password"}   # props of TextField in MUI
    ]
) 
class password(str):  # the new type 
    pass

@funix.funix()
def foo(
    x: password,  # string hidden as asterisks
    y: str        # normal string
    ) -> None: 
    pass
```

The type-to-widget principle allows you to write much shorter code in Funix than in other frameworks. In many cases, you only need the core logic of your app -- which also means you don't have to read any documentation of Funix. 

For example, you can wrap chatGPT API  ....

As another example, below is a comparison of implementing the hangman game in Funix and Gradio, respectively. In the Funix case (left), the only thing besides the core function is adding a friendly prompt to the argument `letter`, which cannot be done using Python's native syntax. In addition, Funix tries to leverage as much of Python's native syntax as possible. Here, we use a `global` variable to maintain the state/session instead of using an additional data type. 

![Gradio vs. Funix](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman_gradio_vs_funix.png)

The UI made in Funix looks like below. By leveraging the Markdown syntax, the output layout can be done easily. 

![Hangman in Funix](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman.png)

## Themes: more than colors and fonts 

A Funix theme defines the mapping from data types to widgets. It further exposes the `props` of the UI components that embody the widgets in JSON so you can control the UI without knowing Javascript.

For example, below is an example theme configure. 

```jsonc
{
  "name": "test_theme",
  "widgets": {    // dict, map types to widgets
    "str": "inputbox",
    "int": "slider[0,100,2]",
    "float": ["slider", { "min": 0, "max": 100, "step": 2 }],
    "Literal": "radio"
  },
  "props": {  // exposing props of UI components
    "slider": { // Funix' sliders are MUI's Sliders
      "color": "#99ff00" // an MUI's Slider has a prop called color
    },
    "radio": { // Funix' radio are MUI's radiobuttons
      "size": "medium" // an MUI's radiobutton has a prop called size
    }
  },
}
```

#### Love Funix? Give us a star

![Borrowed from AppFlowy](https://github.com/AppFlowy-IO/AppFlowy/raw/main/doc/imgs/howtostar.gif)

## Installation

* From PyPI (stable)
    ```bash
    pip install funix
    ```
* From GitHub (latest)

    ```bash
    pip install "git+https://github.com/TexteaInc/funix.git"
    ```
* Local development

    ```bash
    git clone https://github.com/TexteaInc/funix
    cd funix
    pip install -e . 
    ```
    Add `--prefix=~/.local` if pip insists to install to system paths. See [#24](https://github.com/TexteaInc/funix/issues/24) and [#23](https://github.com/TexteaInc/funix/issues/23)
 
## Gallery

More examples in <a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide</a>, <a href="https://github.com/TexteaInc/funix-doc/blob/main/Reference.md">Reference Manual</a>, or the <code>./examples</code> folder.

### ChatGPT, multi-turn

<details>
  <summary>Click me for source code. Just 40 lines! No non-Python-native widget needed. </summary>

  ```python
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

    import funix 
    @funix.funix(
        direction="column-reverse",
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

  ```

</details>

![Multiturn chat](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/chatGPT_multiturn.png)

### Shortest Dall-E web app in Python

```python
from funix import funix                      # add line one
from funix.hint import Images                # add line two
import openai  # pip install openai

openai.api_key = os.environ.get("OPENAI_KEY")

@funix()                                     # add line three
def dalle(prompt: str = "a cat") -> Image:
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return response["data"][0]["url"]
```

![Dalle demo](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/dalle.jpg)

<!-- Funix.io can get the same job done in half the amount of code required by Gradio, by exploiting the Python language as much as possible. Here, state/session is maintained using a global variable, while the order of the returns defines the return layout.  -->

### Web UI for LLMs hosted on HuggingFace

```python
import os, json, typing # Python's native 
import requests # pip install requests

API_TOKEN = os.getenv("HF_TOKEN") # "Please set your API token as an environment variable named HF_TOKEN. You can get your token from https://huggingface.co/settings/token"

def huggingface_(
    model_name: typing.Literal[
        "gpt2", 
        "bigcode/starcoder", 
        "google/flan-t5-large"] = "gpt2", 
    prompt: str = "Who is Einstein?") -> str: 

    payload = {"inputs": prompt} # not all models use this query  and output formats.  Hence, we limit the models above. 

    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.post(API_URL, headers=headers, json=payload)

    if "error" in response.json(): 
        return response.json()["error"]
    else:
        return response.json()[0]["generated_text"]
```

### Compound UIs

```python
from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

@funix(
        widgets={
           "a": "sheet",
           "b": ["sheet", "slider[0,1,0.01]"]
        }
)

# below is a simple matplotlib function
def table_plot(a: List[int], b: List[float]) -> Figure:
    fig = plt.figure()
    plt.plot(a, b)
    return fig
```

![table plot demo static](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/table_plot.png)

### Layout

Code [here](https://github.com/TexteaInc/funix/blob/main/examples/shipping.py)

![shipping example](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/easypost_shipping.png)
   
## Usage

### Command line 

```text
usage: funix [-h] [-H 0.0.0.0] [-p 3000] [-F] [-B] [-l] [-R] [-P] [-d] [-t]
             [-g None] [-r None] [-s None] [--version]
             [file_or_module_name]

Funix: Building web apps without manually creating widgets

    Funix turns your Python function into a web app
    by building the UI from the function's signature,
    based on the mapping from variable types to UI widgets,
    customizable per-widget or kept consistent across apps via themes.

    Just write your core logic and leave the rest to Funix.
    Visit us at http://funix.io

positional arguments:
  file_or_module_name   The Python module containing functions to be turned
                        into web apps by Funix. For example, if your
                        functions are in the file `hello.py`, you should pass
                        `hello.py` here.if you want to turn a module called
                        `hello` into a web app, you should pass `hello` here.

options:
  -h, --help            show this help message and exit
  -H 0.0.0.0, --host 0.0.0.0
                        Host of Funix
  -p 3000, --port 3000  Port of Funix
  -F, --no-frontend     Disable frontend server
  -B, --no-browser      Disable auto open browser
  -l, --lazy            Load functions without decorator
  -R, --recursive       Enable directory mode
  -P, --package         Enable package mode
  -d, --dev             Enable development mode
  -t, --transform       Transform the globals to a session variables
  -g None, --from-git None
                        Import module from git
  -r None, --repo-dir None
                        The directories in the repo that need to be used
  -s None, --secret None
                        The secret key for the full app
  --version, -v         show program's version number and exit

```

The command `funix` above is equivalent to `python -m funix` if you have installed Funix. 

For example, to launch examples in the [`examples`](./examples/) folder, run the following command:

```bash
cd examples
funix examples # same as `python -m funix examples`
funix examples_better # same as `python -m funix examples_better`
```

### Call `funix` in Python

Besides starting Funix servers from the command line, you can also start Funix from Python: 

```python
import funix 
funix.run("localhost", 4010, "examples")
```

### Front-end

Normally, Funix will start the front-end by itself. If you need to develop or debug the front-end (hopefully without scaring you) please go through the following steps:

1. If you haven't finished `git clone`, clone the repo first.
2. `cd funix/frontend`
3. `yarn install`
4. `yarn start`

Now, local Funix is at`http://localhost:3000/`You can just use `yarn funix:start` command to open the front-end bound to port 8080 (the back-end service)

### Exposing a Funix-converted app to the public

```bash
python3 -m funix [module] --host [your_server_ip]
```

### With MUI Pro

If you want to use `DataGridPro` and you have a MUI Pro license:

1. Install Node.js and Yarn;
2. Create a file called `.env` in the `frontend` folder;
3. Add `MUI_PRO_LICENSE_KEY=[your_key]` to the file;
4. Run `yarn funix:build` to build the frontend;
5. Done!

## How to contribute

Funix is open-sourced under the MIT License. Community contribution is not only welcomed but desired. Feel free to fork and make a pull request when you are ready. You can also report bugs, suggest new features, etc. via the [issue tracker](https://github.com/TexteaInc/funix/issues/new).

## Acknowledgement

Funix draws inspiration from FastAPI and Plac: building software interfaces by inferring from function signartures containing type hints. We port this idea from the backend (FastAPI) or the terminal (Python-Fire) to the frontend. We also wanna thank Streamlit, Gradio, PyWebIO, and Pynecone. They inspired us. We are just too lazy to manually define widgets imperatively. Funix’s backend is implemented in Flask and the frontend in Material UI. Lastly, Funix was made possible with the generous investment from Miracle Plus (formerly Y Combinator China) to Textea Inc. 

## Team

The Funix team at Textea consists of:

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
