import inspect
import json
from functools import wraps

import flask

from app import app

__supported_basic_types = ['int', 'float', 'str']
__supported_types = __supported_basic_types + ['dict', 'list']
__decorated_functions_list = list()


@app.get('/list')
async def __textea_export_func_list():
    return {
        "list": __decorated_functions_list,
    }


def textea_export(path: str, **decorator_kwargs):
    def decorator(function: callable):
        function_name = getattr(function, '__name__')
        __decorated_functions_list.append(function_name)

        function_signature = inspect.signature(function)
        function_params = function_signature.parameters
        decorated_params = dict()
        for _, function_param in function_params.items():
            function_arg_name = function_param.name
            function_arg_type_name = getattr(function_param.annotation, '__name__')
            if function_arg_name not in decorated_params.keys():
                decorated_params[function_arg_name] = dict()
            decorated_params[function_arg_name]['type'] = function_arg_type_name
        for decorator_arg_name, decorator_arg_dict in decorator_kwargs.items():
            if decorator_arg_name not in decorated_params.keys():
                decorated_params[decorator_arg_name] = dict()
            if 'possible' in decorator_arg_dict.keys():
                decorated_params[decorator_arg_name]['possible'] = decorator_arg_dict['possible']
            elif 'example' in decorator_arg_dict.keys():
                decorated_params[decorator_arg_name]['example'] = decorator_arg_dict['example']
        decorated_function = {
            "path": '/call/{}'.format(path),
            "decorated_params": decorated_params,
        }

        @app.get('/param/{}'.format(function_name))
        async def function_signature():
            return decorated_function

        @wraps(function)
        async def wrapper():
            request_kwargs = flask.request.form
            function_kwargs = dict()
            for request_arg_name, request_arg in request_kwargs.items():
                function_arg_type = function_params[request_arg_name].annotation
                function_arg_type_name = getattr(function_arg_type, '__name__')
                if request_arg_name in function_params.keys():
                    if function_arg_type_name in __supported_basic_types:
                        function_kwargs[request_arg_name] = function_arg_type(request_arg)
                    elif function_arg_type_name == 'dict' or function_arg_type_name == 'list':
                        function_kwargs[request_arg_name] = json.loads(request_arg)
            wrapped_function = function(**function_kwargs)
            return wrapped_function

        post_wrapper = app.post('/call/{}'.format(path))
        post_wrapper(wrapper)
        wrapper._decorator_name_ = 'textea_export'
        return wrapper

    return decorator
