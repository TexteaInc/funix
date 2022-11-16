# Funix

[![PyPI version](https://badge.fury.io/py/pydatafront.svg)](https://badge.fury.io/py/pydatafront)

Supported Types: `int`, `float`, `str`, `list`, `dict`, `bool`, `typing.List`, `typing.Dict`, `typing.Optional`, `typing.TypedDict`

## Installation

### Direct from Github

```shell
python3 -m pip install "git+https://github.com/TexteaInc/funix.git"
```

### Mannual and local

1. Clone the funix repo
2. Go to the folder of the funix
3. `python3 -m pip install -e .` (This approach may [not work on Ubuntu 22.04](https://github.com/TexteaInc/funix/issues/23) using Python 3.10) or add the funix path into `PYTHONPATH`.

## Usage

Suppose your functions are in `functions.py`.

Then the command below will convert your functions to backend APIs:

```shell
python3 -m funix functions
```

By default, the server runs at `localhost:4010`. If you want to modify, you can use the `--host` option and `--port` option.

```shell
cd examples
python3 -m funix functions --host localhost --port 4010
```

We placed some examples under `examples/examples.py`. You may go to that folder, convert the functions, and fire up a backend server.

```shell
cd examples
python3 -m funix examples
```

## Frontend previews

We also provide a preview at the frontend. It will visualize all functions converted into web forms.

A (delayed) deployed frontend is at pdf.textea.io
This frontend assumes that the backend server runs at `localhost:4010`.

If you prefer to set up the frontend preview manually, please follow the instruction below.

First, install `npm` and `yarn` in whatever way you like. Lots of solutions on the Internet.

Then,

```bash
cd frontend
npm install react-scripts
yarn start
```

Finally you can visit `http://localhost:3000`
