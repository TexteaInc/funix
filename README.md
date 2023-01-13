# Funix

> Your will be done, on earth as it is in heaven. — Matthew, 6:10
> 
> Your code will be done, on the Cloud as it is locally. — Book of Funix, 3:16

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

[简体中文](README.zh-CN.md)

Funix can automatically generate front-end and back-end for your Python functions,
and can be deployed to the cloud. Almost no modification to your original code,
just add a simple `@funix` decorator to your function.

## Installation

### From GitHub

You can install via the following command:

```bash
pip install "git+https://github.com/TexteaInc/funix.git"
```

If you want to install from local:

1. `git clone https://github.com/TexteaInc/funix`
2. `cd funix`
3. `pip install -e .`

### From PyPI

```bash
pip install funix
```

## Usage

```text
usage: funix [-h] [--host HOST] [--port PORT] [--front-port FRONT_PORT] [--no-frontend] this_class main_class

Funix

positional arguments:
  this_class            this class
  main_class            main class to import

options:
  -h, --help            show this help message and exit
  --host HOST           host of frontend & backend
  --port PORT           port of backend
  --front-port FRONT_PORT
                        port of frontend
  --no-frontend         disable frontend
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

