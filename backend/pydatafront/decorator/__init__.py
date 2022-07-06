import inspect
import json
from functools import wraps

import flask

from pydatafront import app

__supported_basic_types = ['int', 'float', 'str']
__supported_types = __supported_basic_types + ['dict', 'list']
__decorated_functions_list = list()
__wrapper_enabled = False


def enable_wrapper():
    global __wrapper_enabled
    if not __wrapper_enabled:
        __wrapper_enabled = True

        @app.get('/list')
        def __textea_export_func_list():
            return {
                "list": __decorated_functions_list,
            }


def textea_export(path: str, config: list, input: list, **decorator_kwargs):
    def decorator(function: callable):
        if __wrapper_enabled:
            function_name = getattr(function, '__name__')
            function_preview = {
                "name": function_name,
                "path": "/param/{}".format(path)
            }
            __decorated_functions_list.append(function_preview)

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
                if 'whitelist' in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]['whitelist'] = decorator_arg_dict['whitelist']
                elif 'example' in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]['example'] = decorator_arg_dict['example']
            decorated_function = {
                "path": '/call/{}'.format(path),
                "decorated_params": decorated_params,
                "input": input,
                "config": config
            }

            get_wrapper = app.get('/param/{}'.format(function_name))
            decorated_function_param_getter = lambda: decorated_function
            decorated_function_param_getter.__setattr__('__name__', '{}_param_getter'.format(function_name))
            get_wrapper(decorated_function_param_getter)

            @wraps(function)
            def wrapper():
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
                if not isinstance(wrapped_function, (str, dict, tuple)):
                    wrapped_function = str(wrapped_function)
                return wrapped_function

            post_wrapper = app.post('/call/{}'.format(path))
            post_wrapper(wrapper)
            wrapper._decorator_name_ = 'textea_export'
        return function

    return decorator
