import inspect
import json
from functools import wraps

import flask

from pydatafront import app
from pydatafront.type import Output, Input

__supported_basic_types = ['int', 'float', 'str']
__supported_types = __supported_basic_types + ['dict', 'list']
__decorated_functions_list = dict()


@app.get('/')
def __textea_export_func_list():
    return __decorated_functions_list


def textea_export(path: str, description: str, name: str, inputs: dict, outputs):
    def decorator(function: callable):
        __decorated_functions_list[path] = {"name": name}

        def get_type(t):
            if type(t) == type:
                return {"$type" : getattr(t, "__name__")}
            elif type(t) == list:
                return {'$type': 'enum', 'value': t}
            elif type(t) == dict:
                if "$type" not in t.keys():
                    return {"$type": "dict", "value": {k: get_type(v) for k, v in t.items()}}
                else:
                    res = {'default': t['default']} if 'default' in t.keys() else {}
                    res.update(get_type(t["$type"]))
                    return res
            else:
                raise 'invalid type'.format(str(t))

        param_types = get_type(inputs)['value']
        decorated_function = {
            "inputs": param_types,
            "outputs": get_type(outputs),
            "description": description
        }

        get_wrapper = app.get('/{}'.format(path))

        def decorated_function_param_getter():
            return decorated_function

        decorated_function_param_getter.__setattr__('__name__', '{}_param_getter'.format(name))
        get_wrapper(decorated_function_param_getter)

        @wraps(function)
        def wrapper():
            request_kwargs = flask.request.json['inputs']
            function_kwargs = {"inputs": Input(), "outputs": Output()}
            for req_arg_name, req_arg_value in request_kwargs.items():
                req_arg_type = param_types[req_arg_name]['$type']
                if req_arg_type in __supported_basic_types:
                    arg_type = inputs[req_arg_name]
                    if isinstance(arg_type, dict):
                        arg_type = inputs[req_arg_name]["$type"]
                    function_kwargs['inputs'].set(req_arg_name, (arg_type(req_arg_value)))
                elif req_arg_type == 'enum' or req_arg_type == 'list':
                    function_kwargs['inputs'].set(req_arg_name, req_arg_value)
                elif req_arg_type == 'dict':
                    function_kwargs['inputs'].set(req_arg_name, req_arg_value)
            function(**function_kwargs)
            wrapped_output = function_kwargs['outputs'].get()
            if not isinstance(wrapped_output, (str, dict, tuple, list)):
                wrapped_output = str(wrapped_output)
            return {"outputs": wrapped_output}

        post_wrapper = app.post('/{}'.format(path))
        post_wrapper(wrapper)
        wrapper._decorator_name_ = 'textea_export'
        return wrapper

    return decorator
