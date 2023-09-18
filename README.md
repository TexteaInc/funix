<h1 align="center">
    <!-- <b> -->
        Funix.io<br>
    <!-- </b> -->
    The laziest way to build AI/data <s>demos</s> apps in Python.
</h1>


<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)
[![](https://dcbadge.vercel.app/api/server/JyANAMUAHM?style=flat)](https://discord.gg/JyANAMUAHM)

<h4><a href="https://youtu.be/qDkzXS270Zo">Intro video</a> | <a href="https://github.com/TexteaInc/funix-doc/blob/main/Reference.md">Reference Manual</a> | <a href="https://github.com/TexteaInc/funix/edit/main/README.md#gallery"> Gallery </a> </h4>

https://github.com/TexteaInc/funix/assets/438579/86868ab5-ed6e-46e5-8dc5-9e3e4a3cdc3f

</div>

<hr>

Funix turns an ordinary Python function into a web app in as simple as one command. 
With Funix, a data/ML engineer can build web apps without any knowledge of UI, UX, or even Funix. 
The UI widgets are generated automatically from the function's signature based on a type-to-widget mapping defined in a theme. The theme may be defined by the UI team and shared across apps.

* **Minimalist**: A Funix app has much shorter code than an app using other frameworks because Funix leverages what's already in Python or Python's ecosystem. 
* **Abstraction**: UI control based on variable types rather than individual variables, for centralized UI styling, simple maintenance, and cross-app reusability and consistency. 
* **Declarative**: Manage all UI aspects using JSON strings.
* **Resourceful**: Bridge integrate popular Python libraries like Matplotlib and IPython with widely-used UI modules such as MUI, and expose UI controls to Python users through JSON.
* **Apps, not demos**: Funix comes with the following features so what you build is not just a demo in your company's Intranet but an app accessible to the entire world: [history](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#call-history),  [access control](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#secret), [multipage apps](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#multipage-apps-and-sessionsstates), session management, and cloud deployment (via [Funix-Deploy](https://github.com/TexteaInc/funix-deploy)).

Funix supports common built-in data types of Python, and major scientific types such as `matplotlib.figure.Figure` or `IPython.display`. The widgets are built on top of popular UI frameworks such as Material UI, and their `props` are explosed for users to configure in JSON without knowledge about React or JavaScript.

## Hello, world!

First, install Funix:

```sh
pip install funix
```

Here is a type-hinted Python function saved in the file `hello.py`:

```python
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Running this command

```bash
funix -l hello.py # -l for lazy mode using all default settings
```

will turn it into a web app running at `http://localhost:3000`:

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)

<!-- > **Note**: The `-l` flag stands for _"lazy"_ meaning that only default settings are used. It cannot be used when your function is decorated by the funix decorator `@funix()` which allows you to customize your app. For more details, please refer to the [reference manual]([docs/Reference.md](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md)). -->

## Hello, Gen AI (in no additional code)!

You can wrap any Python function into a web app in Funix.
We believe that in the Gen AI era, software tools will have very few simple UI widgets, mostly texts, and thus the traditional way to building GUI that requires manually creating widgets for each function I/O is not suitable. Funix is designed to address this problem.
For example, the OpenAI's ChatGPT function below, which str-to-str.

```python
# Filename: chapGPT_lazy.py
import os # Python's native
import openai  # you cannot skip it

openai.api_key = os.environ.get("OPENAI_KEY")

def ChatGPT(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    return completion["choices"][0]["message"]["content"]
```

With the magical command `funix -l chatGPT_lazy.py`, you will get a web app like this:
![screenshots/ChatGPT_lazy.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/chatGPT_lazy.png)

#### Love Funix? Give us a star

![Borrowed from AppFlowy](https://github.com/AppFlowy-IO/AppFlowy/raw/main/doc/imgs/howtostar.gif)

## Zen: The types become widgets 

The Zen of Funix is to choose widgets for function I/Os based on their types, instead of picking and customizing a widget for each I/O. In this sense, **Funix to Python is like CSS to HTML or macros to LaTeX**. Ideally, a Data Scientist or a Machine Learning Engineer should NOT touch anything UI -- that's the job of the UI team. The example below shows how four common Python's built-in data types are mapped to widgets.


```python
import typing

import funix

def my_chatbot(
    prompt: str, 
    advanced_features: bool = False,
    model: typing.Literal['GPT-3.5', 'GPT-4.0',
        'Llama-2', 'Falcon-7B']= 'GPT-4.0', 
    max_token: range(100, 200, 20)=140 
    )  -> str:
    pass
```

![four input types](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/input_widgets.png)

### Defining your own types (coming soon)

You can **define your own types and associate widgets to them**, just like in CSS you can define a class or in LaTeX you can define a new control command. For example, the `str` type is mapped to a single-line text input box where the text is displayed as you type. It is not suitable for passwords or API tokens. The code below defines a new type `password` that replaces characters with asterisks.

```python
import funix

@funix.new_funix_type(
    widget=[
        "@mui/material/TextField", # the component in MUI
        {"type":"password"}   # props of TextField in MUI
    ]
)
class password(str):  # the new type, inherited from str
    pass

@funix.funix()
def foo(
    x: password,  # string hidden as asterisks
    y: str        # normal string
    ) -> None:
    pass
```

### Being lazy: less (code) is better
**The type-to-widget zen of Funix means writing less code.** Often, you only need the core logic of your app. In contrast, in other frameworks, the same function I/O needs to appear twice: once in the function's signature, and the other time in the widget creation code. If you modify the interface of the function, you have to modify the widget creation code as well. This is redundant and doubles the effort.

For example, below is the implementation of the hangman game in Funix (left) and Gradio (right), respectively. In the Funix case (left), the only thing besides the core function is adding a friendly prompt to the argument `letter`, which cannot be done using Python's native syntax. In addition, Funix leverages as much of Python's native syntax as possible. Here, we use a `global` variable to maintain the state/session and even passing values across pages/functions.

![Gradio vs. Funix](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman_gradio_vs_funix.png)

The UI made in Funix looks like below. By leveraging the Markdown syntax, the output layout can be done easily.

![Hangman in Funix](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman.png)

## Themes: more than colors and fonts

A Funix theme defines the mapping from data types to widgets. It further exposes the `props` of the UI components that embody the widgets in JSON so you can control the UI without knowing Javascript. Most of components used in Funix are from Material UI.

For example, below is an example theme configure. To know more about how to define and apply a theme, please refer to [the Themes section in the reference manual](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#themes). 

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

## Features to build apps instead of demos 

### History: Keep your call logs

<details>
<summary>
Click to expand
</summary>

A feature request that we hear from many users is that they do not use a Funix-converted app as a demo that they will use only a couple of time but as a real app that they will use again and again. In this case, they want to keep the call history of the app. Funix supports this feature by default. You can access the history of your app by clicking the history button on the top right corner of the app. 

![history sidebar](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/history_sidebar.gif)

</details>

### Multipage data passing and session/state management

<details>
<summary>
Click to expand
</summary>

A real app usually comes with multiple page, e.g., setting OpenAI token key in one page and then use the token in other GenAI pages. Functions in the same `.py` script will become different pages of one app. Any global variable can be used to pass data between functions. When you start Funix with the flag `-t`, it will further sessionize the global variables so that different users can have their own sessions. Below is a simple example and the corresponding GIF animation. In the GIF animation you can see that the value `y` differs in two browser sessions. 

```python
import funix

y = "The default value of y."

@funix.funix()
def set_y(x: str="123") -> str:
    global y
    y = x
    return "Y has been changed. Now check it in the get_y() page."


@funix.funix()
def get_y() -> str:
    return y
```

![session](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/session.gif)

</details>

### Prefill

<details>
<summary>
Click to expand
</summary>

A special case of passing data between functions is to use the return value of one function as the value in the widget of an argument of another function. This is called prefill. Funix support prefill by using a decorator attribute `pre_fill`. Below is an example and the corresponding GIF animation.


```python
import funix

def first_action(x: int) -> int:
  return x - 1

def second_action(message: str) -> list[str]:
  return message.split(" ")

def third_action(x: int, y: int) -> dict:
  return {"x": x, "y": y}

@funix.funix(
  pre_fill={
    "a": first_action,
    "b": (second_action, -1),
    "c": (third_action, "x")
  }
)
def final_action(a: int, b: str, c: int) -> str:
    return f"{a} {b} {c}"
```

<!-- FIXME: ADD GIF IMAGE HERE -->
</details>

### Secret: Access control

<details>
<summary>
Click to expand
</summary>

> Note: This is not a strong way to protect your app.

To protect your code (e.g., OpenAI-related functions, which may result in some financial loss), you can use the `secret` option.

```bash
funix  my_app.py --secret  my_secret_token # use a token provided by you
# or 
funix  my_app.py --secret  True # randomly generate a token
```

The token will be printed on the Terminal. For example,

```bash
$ funix hello.py --secret True
Secrets:
---------------
Name: hello
Secret: 8c9f55d0eb74adbb3c87a445ea0ae92f
Link: http://127.0.0.1:3000/hello?secret=8c9f55d0eb74adbb3c87a445ea0ae92f
```

The token needs to be included in the URL or manually entered in order to execute the app. 

![secret](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/secret.gif)

</details>

## Gallery

More examples in <a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide</a>, <a href="https://github.com/TexteaInc/funix-doc/blob/main/Reference.md">Reference Manual</a>, or the <code>./examples</code> folder.

* [ChatPaper](https://github.com/forrestbao/ChatPaper) (It's like the popular ChatPDF. But in Funix, only 70 lines of code needed.)
* [mFlux](https://github.com/Yazawazi/MFlux) (synthetic biology)

### Chatbot from any generative LLMs on HuggingFace

<details>
<summary><code>examples/AI/huggingface.py</code> 👈 Toggle me to show source code </summary>

```python
import os, json, typing # Python's native
import requests # pip install requests

API_TOKEN = os.getenv("HF_TOKEN") # "Please set your API token as an environment variable named HF_TOKEN. You can get your token from https://huggingface.co/settings/token"

def huggingface(
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
</details>

![Multiturn chat](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/huggingface.png)

### ChatGPT, multi-turn
<details>
  <summary><code>examples/AI/chatGPT_multi_turn.py</code> 👈 Toggle me to show source code </summary>

  ```python
    import os
    import IPython     
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
    def ChatGPT_multi_turn(current_message: str)  -> IPython.display.HTML:
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
    response = openai.Image.create(prompt=prompt)
    return response["data"][0]["url"]
```

![Dalle demo](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/dalle.jpg)

<!-- Funix.io can get the same job done in half the amount of code required by Gradio, by exploiting the Python language as much as possible. Here, state/session is maintained using a global variable, while the order of the returns defines the return layout.  -->


### Compound UIs

The table is copi-able from Excel! The plot is interactive!

<details>
<summary><code>examples/slider_table_plot.py</code> 👈 Toggle me to show source code</summary>

> The code below uses an inelegant solution by manually choosing the `sheet` widget. We are working on a better solution by feeding a Pandas DataFrame to the `table_plot` function to automate. 

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

</details>

![table plot demo static](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/table_plot.png)

### Bioinformatics: vector stripping

[<code>examples/bioinformatics/vector_strip.py</code>](./examples/bioinformatics/vector_strip.py) 👈 Click to see source code

![bioinfo vector strip](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/bioinfo_vector_strip.png)

### Multimedia inputs and outputs

<details>
<summary><code>examples/multimedia/rgb2gray.py</code> 👈 Toggle me to show source code</summary>

```python
import  io # Python's native

import PIL # the Python Image Library
import funix

@funix.funix(
    title="Convert color images to grayscale images",
)
def gray_it(image: funix.hint.BytesImage) -> funix.hint.Image:
    img = PIL.Image.open(io.BytesIO(image))
    gray = PIL.ImageOps.grayscale(img)
    output = io.BytesIO()
    gray.save(output, format="PNG")
    return output.getvalue()
```
</details>

![shipping example](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/rgb2gray.png)

### Layout and EasyPost shipping

[`examples/layout_easypost_shipping.py`](./examples/layout_easypost_shipping.py) 👈 Click me to see source code

![shipping example](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/easypost_shipping.png)

## Usage

### Installation

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

### Building the frontend

In the last two cases above, you will need to compile the frontend by yourself. Suppose you are in the `funix` folder. Then run the following commands:

1. `cd frontend`
3. `yarn install`
4. `yarn start`

#### Building the frontend with MUI Pro

Our table widget uses advanced features in MUI Pro. If you have a MUI Pro license, you can build the frontend with MUI Pro by following the steps below:

1. Install Node.js and Yarn;
2. Create a file called `.env` in the `frontend` folder;
3. Add `MUI_PRO_LICENSE_KEY=[your_key]` to the file;
4. Run `yarn funix:build` to build the frontend;
5. Done!

### Command line options

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

### Call `funix` in Python

Besides starting Funix from the command line, you can also use a self-contained `.py` script:

```python
import funix

@funix.funix()
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."

if __name__ == "__main__":
    funix.run(__file__)
```

### Exposing a Funix-converted app to the public

```bash
funix [module] --host [your_server_ip]
```

## How to contribute

Funix is open-sourced under the MIT License. Community contribution is not only welcomed but desired. Feel free to fork and make a pull request when you are ready. You can also report bugs, suggest new features via the [issue tracker](https://github.com/TexteaInc/funix/issues/new) or our [Discord server](https://discord.gg/JyANAMUAHM).

## Acknowledgement

Funix draws inspiration from FastAPI and Plac: building software interfaces by inferring from function signartures containing type hints. We port this idea from the backend (FastAPI) or the terminal (Python-Fire) to the frontend. We also wanna thank Streamlit, Gradio, PyWebIO, and Pynecone. They inspired us. We are just too lazy to manually define widgets imperatively. Funix’s backend is implemented in Flask and the frontend in Material UI. Lastly, Funix was made possible with the generous investment from Miracle Plus (formerly Y Combinator China) to Textea Inc.

## Team

The Funix team at Textea consists of:

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
