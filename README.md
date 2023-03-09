<h1 align="center">
    <b>
        Funix.IO<br>
    </b>
    ⭐️  The laziest way to build web apps in Python.  ⭐️ <br>
</h1>



<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

<h4><a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide</a> | <a href="https://textea.notion.site/Funix-Reference-Manual-452a8ce51bdf4c29b4650bed7df270f6">Reference Manual</a> | <a href="https://github.com/TexteaInc/funix/blob/main/README.zh-CN.md">简体中文</a>
 </h4>

![](https://github.com/TexteaInc/funix-doc/blob/main/videos/chatgpt/scence_1_ChatGPT_in_two_lines/chatgpt_1.gif?raw=true)
</div>

## Features

Funix is designed for an algorithm/ML engineer to build web apps without writing code related to the UI, not even selecting a widget and passing it to or calling it in a Python function. 

* Generating web app UI from the signature of a Python function.
* Inferring widgets from variable types. No manual widget selection needed.
* Type-to-widget mapping stored in themes for cross-app UI consistency. 
* Declarative UI customization when needed. 
* Non-intrusive. You can still run or debug your Python code locally as usual.
 


> **WIP**: Funix is still under development. If you have any questions, please feel free to [open an issue](https://github.com/TexteaInc/funix/issues/new).


## Hello-world in Funix 

Add as few as two lines of code above your function to vitialize it into a web app.

```python
from funix import funix # add line one

@funix()                # add line two
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Save the code above as `hello.py`.
Then run this at the terminal:

```bash
funix hello
```

A web app will be launched at `http://localhost:3000` and automatically opened in a browser window.

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)


## Gallery

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

### Declarative UI configuration

In Funix, your UI configurations are not intermingled with the functions under UI components. They can be put into configuration files or in themes.

```python
from funix import funix_yaml

@funix_yaml("""
    widgets:
        x: slider[0,10,1]
        op: radio
""")

def power(x: int, op: str) -> Markdown:
    if op =="square":
        return  f"\
* The _square_ of {x} is **{x * x}**. \n \
* Made by [Funix](http://funix.io)"
    elif op == "cube":
        # return x * x * x
        return  f"\
* The _cube_ of {x} is **{x * x * x}**. \n \
* Made by [Funix](http://funix.io)"
```

![power slider radio](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/power_slider_radio.png)

## More examples
1. [QuickStart Guide](https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md)
2. The [`examples` folder in this repo](./examples/)

## Installation

### From PyPI (stable)

```bash
pip install funix
```

### From GitHub (latest)

```bash
pip install "git+https://github.com/TexteaInc/funix.git"
```

### Local development

If you want to install Funix from a local clone:

1. `git clone https://github.com/TexteaInc/funix`
2. `cd funix`
3. `pip install -e .` (add `--prefix=~/.local` if pip insists to install to system paths. See [#24](https://github.com/TexteaInc/funix/issues/24) and [#23](https://github.com/TexteaInc/funix/issues/23))


## Usage

### Command line 

```text
funix [-h] [-H 127.0.0.1] [-p 3000] [-F] [-B] 

Funix: Building web apps without manually creating widgets

positional arguments:
  main_class            The Python module containing functions 
                        to be turned into web apps by Funix 

options:
  -h, --help            show this help message and exit
  -H 127.0.0.1, --host 127.0.0.1
                        Host of frontend and backend
  -p 3000, --port 3000  Port of frontend and backend
  -F, --no-frontend     Disable frontend server
  -B, --no-browser      Disable auto open browser
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

## Stay up-to-date
![Borrowed from AppFlowy](https://github.com/AppFlowy-IO/AppFlowy/raw/main/doc/imgs/howtostar.gif)

## How to contribute

Funix is open-sourced under the MIT License. Community contribution is not only welcomed but desired. Feel free to fork and make a pull request when you are ready. You can also report bugs, suggest new features, etc. via the [issue tracker](https://github.com/TexteaInc/funix/issues/new).

## Acknowledgement

Funix draws inspiration from FastAPI and Plac: building software interfaces by inferring from function signartures containing type hints. We port this idea from the backend (FastAPI) or the terminal (Python-Fire) to the frontend. We also wanna thank Streamlit, Gradio, PyWebIO, and Pynecone. They inspired us. We are just too lazy to manually define widgets imperatively. Funix’s backend is implemented in Flask and the frontend in Material UI. Lastly, Funix was made possible with the generous investment from Miracle Plus (formerly Y Combinator China) to Textea Inc. 

## Team

The Funix team at Textea consists of:

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
