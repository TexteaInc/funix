# Funix -- Building web apps without manually creating widgets

> Your will be done, on earth as it is in heaven. — Matthew, 6:10
>
> Your code be run, on the Cloud as it is locally. — Book of Funix, 3:16

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

[简体中文](README.zh-CN.md)

Funix automatically turns an ordinary Python function into a web app without needing you to specify any widgets.
Simply add a `@funix` decorator above your function and then it becomes an app in the browser for anyone, without coding skills, to use.


Funix supports complex data types/widgets, such as multi-column data tables or Matplotlib chats.
Funix is non-intrusive. You can still run or debug your Python code locally as usual.
Funix also has a backend, for its own frontend as well as those who wants to turn Python functions into RESTful APIs.

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
3. `pip install -e .` (add `--prefix=/.local` if pip insists to install to system paths. See [#24](https://github.com/TexteaInc/funix/issues/24) and [#23](https://github.com/TexteaInc/funix/issues/23))



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
There are some simple examples in the `examples` folder to help you understand Funix.
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
