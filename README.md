# PyDataFront

Supported Types: `int`, `float`, `str`, `list`, `dict`

## Installation


```shell
python3 -m pip install "git+https://github.com/TexteaInc/PyDataFront.git" 
```

## Usage 

Suppose your functions are in `functions.py`. 

Then the command below will convert your functions to backend APIs:

```shell
python3 -m pydatafront functions 
```

By default, the server runs at `localhost:4010`. If you want to modify, you can use the `--host` option and `--port` option. 

```shell
cd examples
python3 -m pydatafront functions --host localhost --port 4010
```

We placed some examples under `examples/examples.py`. You may go to that folder, convert the functions, and fire up a backend server. 

```shell
cd examples
python3 -m pydatafront examples 
```


## Frontend previews

We also provide a preview at the frontend. It will visualize all functions converted into web forms. 
This frontend assumes that the backend server runs at `localhost:4010`. 

First, install `npm` and `yarn` in whatever way you like. Lots of solutions on the Internet. 

Then, 
```
cd frontend
npm install react-scripts
yarn start 
```

Finally you can visit http://localhost:3000
