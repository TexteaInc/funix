<h1 align="center">
    <b>
        Funix.IO<br>
    </b>
    ⭐️  The laziest way to build AI/data apps in Python.  ⭐️ <br>
</h1>


<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

<h4><a href="https://youtu.be/DVIV_EUFNbw">Intro video</a> | <a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide</a> | <a href="https://textea.notion.site/Funix-Reference-Manual-452a8ce51bdf4c29b4650bed7df270f6">Reference Manual</a> | <a href="https://github.com/TexteaInc/funix/edit/main/README.md#gallery"> Gallary </a> </h4>

https://user-images.githubusercontent.com/438579/236646521-30ed67f4-4708-4cf1-858d-33b65bc53b6a.mp4

</div>

## Features

Funix is designed for an algorithm/ML engineer to build apps without writing code related to the UI, not even selecting a widget and passing it to or calling it in a Python function. 

* **Minimalist**: Automatic UI generation. No manual widget selection.
* **Centralized styling**: Type-to-widget mapping stored in themes for cross-app UI consistency. 
* **Declarative**: All non-default controls, including UI customization, via Python dictionaries. 
* **Non-intrusive**: You can still run or debug your Python code locally as usual.

> **WIP**: Funix is still under development. If you have any questions, please feel free to [open an issue](https://github.com/TexteaInc/funix/issues/new).

## Hello, world in Funix 

Building a web app in Funix is super easy. Just have a type-hinted Python function: 

```python
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Save in a file (say `hello.py`) and pass to Funix:

```bash
funix -l hello.py
```

A web app will be launched at `http://localhost:3000` and automatically opened in a browser window.

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)

> **Note**: The `-l` flag stands for _"lazy"_ meaning that only default settings are used. It cannot be used when your function is decorated by the funix decorator `@funix()` which allows you to customize your app. Advanced examples below use decorators. For more details of the decorator values, please refer to the [reference manual](docs/Reference.md).

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

More examples in <a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">QuickStart Guide</a> or the <code>examples</code> folder.

### ChatGPT, multi-turn

Code [here](https://github.com/TexteaInc/funix-examples/blob/main/AI/chatGPT_multi_turn.py). Just 77 lines including the HTML layout code and tip messages. 

![Multiturn chat](https://raw.githubusercontent.com/TexteaInc/funix-examples/main/screenshots/AI/chatGPT_multi_turn.png)

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

### Layout

Code [here](https://github.com/TexteaInc/funix/blob/main/examples/shipping.py)

![shipping example](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/easypost_shipping.png)
   
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

## How to contribute

Funix is open-sourced under the MIT License. Community contribution is not only welcomed but desired. Feel free to fork and make a pull request when you are ready. You can also report bugs, suggest new features, etc. via the [issue tracker](https://github.com/TexteaInc/funix/issues/new).

## Acknowledgement

Funix draws inspiration from FastAPI and Plac: building software interfaces by inferring from function signartures containing type hints. We port this idea from the backend (FastAPI) or the terminal (Python-Fire) to the frontend. We also wanna thank Streamlit, Gradio, PyWebIO, and Pynecone. They inspired us. We are just too lazy to manually define widgets imperatively. Funix’s backend is implemented in Flask and the frontend in Material UI. Lastly, Funix was made possible with the generous investment from Miracle Plus (formerly Y Combinator China) to Textea Inc. 

## Team

The Funix team at Textea consists of:

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
