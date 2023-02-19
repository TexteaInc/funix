# Funix -- The laziest way to build web apps in Python

Funix automatically turns an ordinary Python function into a web app without needing you to specify any widgets. (See quick examples)
Simply add a `@funix` decorator above your function and then it becomes an app in the browser for anyone, without coding skills, to use.

Funix supports complex data types/widgets, such as multi-column data tables or Matplotlib chats.
If you need to customize the UI, do it declaratively.
Funix is non-intrusive. You can still run or debug your Python code locally as usual.


<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

<h3><a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide and showcase</a>  </h3>

[简体中文](README.zh-CN.md)

https://user-images.githubusercontent.com/438579/219586150-7ff491dd-dfea-41ea-bfad-4610abf1fe20.mp4 <br>
<a href="https://www.youtube.com/watch?v=UGp5gbR8f3c">Watch on YouTube</a>

<br /><br />

</div>


> **WIP**: Funix is still under development, if you have any questions, please feel free to [open an issue](https://github.com/TexteaInc/funix/issues/new).


## Usage 

Add as few as two lines of code above your function and then the function is vitialized into a web app. 

```python
from funix import funix # add line one

@funix()                # add line two 
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Save the code above as `hello.py`.
Then run this at the terminal:

```bash
python3 -m funix hello
```

A web app will be launched at `http://localhost:80` (use ``-P {PORT Number}` if you are not root or sudo) and automatically opened in a browser window.

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)


## Gallery

### Shortest Dall-E web app in Python

```python
from funix import funix                      # add line one 
from funix.hint import Images                # add line two
import openai  # pip install openai

openai.api_key = os.environ.get("OPENAI_KEY")

@funix()                                     # add line three 
def dalle(prompt: str = "a cat") -> Images:  
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
    whitelist:
        op: 
            - square
            - cube
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


## Installation

### From PyPI

```bash
pip install funix
```

### From GitHub

```bash
pip install "git+https://github.com/TexteaInc/funix.git"
```

### Local development

If you want to install Funix from a local clone:

1. `git clone https://github.com/TexteaInc/funix`
2. `cd funix`
3. `pip install -e .` (add `--prefix=~/.local` if pip insists to install to system paths. See [#24](https://github.com/TexteaInc/funix/issues/24) and [#23](https://github.com/TexteaInc/funix/issues/23))


## Usage

```text
usage: funix [-h] [--host HOST] [--port PORT] [--front-port FRONT_PORT] [--no-frontend] [--no-browser]
             this_class main_class

Funix

positional arguments:
  this_class            this class
  main_class            main class to import

options:
  -h, --help            show this help message and exit
  --host HOST, -H HOST  host of frontend & backend
  --port PORT, -p PORT  port of backend
  --front-port FRONT_PORT, -P FRONT_PORT
                        port of frontend
  --no-frontend, -F     disable frontend
  --no-browser, -B      disable auto open browser
```

Usually you can use `python -m funix [module]` to start directly.
There are some simple examples in the [`examples`](./examples/) folder to help you understand Funix.
You can open the example by the following command:

```bash
cd examples
python -m funix examples
python -m funix examples_better # Examples V2 😄
```

## Build Frontend

In Funix, we have packaged a frontend that you can use directly,
and we also have a frontend page that is deployed on the [public](https://pdf.textea.io/).
If you want to build the frontend yourself, you can do so with the following command:

```
# Please clone the repository first and enter the repository directory
cd frontend
yarn install # Install dependencies
yarn build # Build frontend server
yarn funix:build # Build to Funix Python folder
yarn funix:test # Start Funix frontend server (automatically set backend server to http://127.0.0.1:8080)
```

## How to contribute 

Funix is open-sourced under the MIT License. Community contribution is not only welcomed but desired. Feel free to fork and make a pull request when you are ready. You can also report bugs, suggest new features, etc. via the [issue tracker](https://github.com/TexteaInc/funix/issues/new).

## Acknowledgement
We were inspired by FastAPI's approach of using type hints to build apps. We also want to thank Streamlit, Gradio, PyWebIO, and Pynecone for their influence on the development of Funix. Our backend is implemented using Flask, and the front-end primarily using Material UI. Lastly, Funix was made possible with the generous investment from Miracle Plus (formerly Y Combinator China) to Textea Inc. tel

## Team
The Funix team at Textea consists of:
* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)