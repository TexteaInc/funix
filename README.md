<h1 align="center">
    <!-- <b> -->
        Funix.io<br>
    <!-- </b> -->
    The laziest way to build AI/Data apps in Python
</h1>


<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)
[![](https://dcbadge.vercel.app/api/server/JyANAMUAHM?style=flat)](https://discord.gg/JyANAMUAHM)

<h4><a href="https://youtu.be/qDkzXS270Zo">Intro video</a> | <a href="https://github.com/TexteaInc/funix-doc/blob/main/Reference.md">Reference Manual</a> | <a href="#gallery"> Gallery </a> </h4>

https://github.com/TexteaInc/funix/assets/438579/86868ab5-ed6e-46e5-8dc5-9e3e4a3cdc3f

</div>

## What is Funix? 

* Funix automatically turns an ordinary Python function or class definition into a web app, which is accessible in a browser via a shareable link. 
* Funix is the frontend/backend/fullstack engineer and the infra/ops engineer for AI/Data/Science solo stars like you. 
* Funix is the no-/low-code solution for those who write the most core and innovative code. 
* Funix is open-source and can be deployed on-premises. 

## Use cases
* Startups: quickly build demos, iterate on MVPs, get user feedback and statistics, and pitch to investors or your mom. 
* Generative AI: instantly allow people to interact your GenAI model or idea.
* STEM research: let people run your model and/or algorithm effortlessly. 
* Data browser: an interface to page through your data. 
* A/B test and data labeling: collect human labeling or preference.

## Key advantages

* **Minimalist and effortless**: Make no or little addition to your existing code. 
* **CSS for Python**: Widgets are generated automatically based on variable types according to a theme, rather than per-variable manually, for centralized, reusable, and consistent UI across apps. 
* **Non-intrusive and Declarative**: In JSON string, UI aspects are separated from the core logic. Your code can still be run, imported, and called as usual. 
* **Seamlessly Pythonic**: Map Python's native keywords to web app features, such as `global` for sessions, `yield` for streaming, and `print` for anything you wanna display in your app. 
* **Apps, not demos**: Out of the box support for [history](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#call-history), [access control](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#secret), [multipage apps](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#multipage-apps-and-sessionsstates), session management, reactiveness, backend telemetry, passing values between widgets and pages, etc.

#### Love Funix? Give us a star

![Borrowed from AppFlowy](https://github.com/AppFlowy-IO/AppFlowy/raw/main/doc/imgs/howtostar.gif)

## Hello, world!

1. Install Funix ([advanced installation options](#installation)):

    ```sh
    pip install funix
    ```

2. Save the code bellow to a file called `hello.py`:

    ```python
    def hello(your_name: str) -> str:
        return f"Hello, {your_name}."
    ```

3. Running this command

    ```bash
    $ funix -l hello.py # -l for lazy mode using all default settings
    ```

4. The app will pop in a browser on `http://localhost:3000`:

    ![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)


<!-- > **Note**: The `-l` flag stands for _"lazy"_ meaning that only default settings are used. It cannot be used when your function is decorated by the funix decorator `@funix()` which allows you to customize your app. For more details, please refer to the [reference manual]([docs/Reference.md](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md)). -->

## A quick showoff of Funix

**The Zen of Funix** is to generate widgets for function I/Os based on their types, instead of manually picking and customizing the widget for each I/O. **Funix to Python is like CSS to HTML or style class to LaTeX**. UI stuff is not intermingled with the core logic but defined separately. The type-to-widget mapping is controlled by a theme and new types can be defined on top of existing types. 


The example below shows how common UI compoents are generated from four Python-native data types: `str`, `bool`, `Literal` and `range`, as well as types in popular packages such as `ipywidgets.Password`. The example below further maps default values to placeholders in the UI widgets. From this example, we can see that developers need to **learn nothing about Funix or do nothing to their existing code** before they can get an app. 


```python
import typing # Python native 

import ipywidgets  # popular UI library 

def input_widgets_basic(
    prompt: str = "Who is Oppenheimer?",
    advanced_features: bool = True,
    model: typing.Literal['GPT-3.5', 'GPT-4.0', 'Falcon-7B'] = 'GPT-4.0',
    max_token: range(100, 200, 20) = 140,
    openai_key: ipywidgets.Password = "1234556",
    )  -> str:
    pass
```

![four input types](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/input_widgets.png)

The example below shows how `pandas.DataFrame` and `matplotlib.figure.Figure` that AI/data developers cannot be more familiar with are mapped to tables and charts in an app. 

```python
import pandas, matplotlib.pyplot
from numpy import arange, log
from numpy.random import random

def table_and_plot(
    df: pandas.DataFrame = pandas.DataFrame({
        "a": arange(500) + random(500)/5,
        "b": random(500)-0.5 + log(arange(500)+1),
        "c": log(arange(500)+1) })
    ) -> matplotlib.figure.Figure:

    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(df["a"], df["b"], 'b')
    matplotlib.pyplot.plot(df["a"], df["c"], 'r')

    return fig
```

![table and plot screenshot](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/table_plot.png)

 

### Funix and classes

Funix can turn each member method of a class into a page of an app. 
In two additional lines, the example turn a class definition into a multi-page app with the OOP experience where the instantiation of an object of the class is done in a page corresponding to the constructor of the class and the member values of the object can be viewed and updated in other pages. 

```python
from funix import funix_class

@funix_class()  
class A:
    def __init__(self, a: int):
        self.a = a
        return f"`self.a` has been initialized to {self.a}"

    def update_a(self, b: int) -> str:
        self.a = b
        return f"`self.a` has been updated to {self.a}"

    def print_a(self) -> str:
        return f"The value of `self.a` is {self.a}"
```

![class demo app gif](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/videos/class/class.gif)


A more advanced example of class is the wordle game. You can find the source code in [`examples/wordle.py`](./examples/wordle.py). The screenshot is as follows:



### The quickest way to build GenAI apps

You can wrap any Python function into a web app in Funix.
For example, you can take the ChatGPT demo code from OpenAI's APi reference and wrap it into a str-to-str function: 

```python
# command: funix -l chatgpt.py
from openai import OpenAI

def ChatGPT(prompt: str) -> str:    
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
return completion.choices[0].message
```
which is turned into an app by Funix like below: 

![screenshots/ChatGPT_lazy.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/chatGPT_lazy.png)




### Themes: the CSS for Python 

**Funix to Python is like CSS to HTML or macros to LaTeX.** It separates the core logic and the UI. 
All UI stuff is centrally defined in a JSON-based theme to avoid the repetitiveness of individually configuring widgets and keep a consistent look across apps. Consequently, a data scientist or a machine learning engineer does not need to think about anything UI. Just leave it to the UI team and Funix. 

Below is an example of a theme file. It defines the widget choices based on variable types and tweaks the `props` of UI components (currently only MUI ones are supported). To know more about how to define and apply a theme, please refer to [the Themes section in the reference manual](https://github.com/TexteaInc/funix-doc/blob/main/Reference.md#themes). 

```jsonc
{
  "name": "test_theme",
  "widgets": {    // dict, map types to widgets
    "str": "inputbox",
    "int": "slider[0,100,2]",
    "float": ["slider", { "min": 0, "max": 100, "step": 2 }],
    "Literal": "radio"
  },
  "props": {  // props of UI components
    "slider": { // Funix' sliders are MUI's Sliders
      "color": "#99ff00" // an MUI's Slider has a prop called color
    },
    "radio": { // Funix' radio are MUI's radiobuttons
      "size": "medium" // an MUI's radiobutton has a prop called size
    }
  },
}
```

To introduce a new data type, just declare a new Python class, and use a decorator to let Funix know. You can associate the type with a widget either on-the-fly (below) or via a theme file. 

```python
from funix import funix, new_funix_type

@new_funix_type(
        widget = {"name":"password"}
    ) # associate the new type `blackout_message` to the widget `password`
class blackout_message(str): # inherit from str
    def print(self):
        return self + " is from Funix"

@funix()
def hoho(x: blackout_message):
    return x.print()

# Still works as usual
if __name__ == "__main__":
    print (hoho(warning_message('Fun'))) 
```

## Python native to web native

Funix is designed to be as Pythonic as possible. It maps Python's native keywords to web app features.

### `print` to add content to the app

```python
from funix import funix
@funix(
    print_to_web=True
)
def my_main(x: str="123", debug:bool=True) -> None:
    if debug:
        print("### This is a debug message.")
    return None
```

## Advanced features 

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

* From PyPI (stable, lacking the latest feature)
    ```bash
    pip install funix
    ```
* From GitHub (latest)

    ```bash
    pip -b develop install "git+https://github.com/TexteaInc/funix.git"
    ```
* Local development

    ```bash
    git clone -b develop https://github.com/TexteaInc/funix
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
usage: funix [-h] [-H 0.0.0.0] [-p 3000] [-F] [-B] [-l] [-P] [-d] [-t] [-g None] [-r None] [-s None] [-D None] [--version] [file_folder_or_module_name]

Funix: Building web apps without manually creating widgets

    Funix turns your Python function into a web app
    by building the UI from the function's signature,
    based on the mapping from variable types to UI widgets,
    customizable per-widget or kept consistent across apps via themes.

    Just write your core logic and leave the rest to Funix.
    Visit us at http://funix.io

positional arguments:
  file_folder_or_module_name
                        The Python module containing functions to be turned into web apps by Funix. For example, if your functions are in the file `hello.py`, you should pass `hello.py` here. if you want to turn a module called `hello` into a web app, you should pass `hello`
                        here, and with --package or -P flag. if you want to turn a full folder called `examples` into a web app, you should pass `examples` here.

options:
  -h, --help            show this help message and exit
  -H 0.0.0.0, --host 0.0.0.0
                        Host of Funix
  -p 3000, --port 3000  Port of Funix
  -F, --no-frontend     Disable frontend server
  -B, --no-browser      Disable auto open browser
  -l, --lazy            Load functions without decorator
  -P, --package         Enable package mode
  -d, --dev             Enable development mode
  -t, --transform       Transform the globals to a session variables
  -g None, --from-git None
                        Import module from git
  -r None, --repo-dir None
                        The directories in the repo that need to be used
  -s None, --secret None
                        The secret key for the full app
  -D None, --default None
                        The default function to run
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

Funix draws inspiration from FastAPI and Python-Fire: building software interfaces by inferring from function signatures containing type hints. We port this idea from the backend (FastAPI) or the terminal (Python-Fire) to the frontend. We also thank Streamlit, Gradio, PyWebIO, and Pynecone/Reflex. They inspired us. We are just too lazy to manually define widgets imperatively. Funix’s backend is implemented in Flask and the frontend in Material UI. 

## Team

Funix is a team effort of: 

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
