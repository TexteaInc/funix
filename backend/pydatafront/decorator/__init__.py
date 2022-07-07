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


def textea_export(path: str, **decorator_kwargs):
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
            output_type = getattr(function_signature.return_annotation, '__name__')
            decorated_params = dict()

            if 'output_dict' in decorator_kwargs.keys():
                output_type = dict()
                for key, tp in decorator_kwargs['output_dict'].items():
                    output_type[key] = getattr(tp, '__name__')
                decorator_kwargs.pop('output_dict')

            input=[]
            config=[]
            input_attr=""
            for decorator_arg_name, decorator_arg_dict in decorator_kwargs.items():
                if decorator_arg_name not in decorated_params.keys():
                    decorated_params[decorator_arg_name] = dict()
                if decorator_arg_dict['treat_as'] == 'config':
                    decorated_params[decorator_arg_name]['treat_as'] = 'config'
                else:
                    decorated_params[decorator_arg_name]['treat_as'] = decorator_arg_dict['treat_as']
                    input_attr = decorator_arg_dict['treat_as'] if input_attr == '' else input_attr
                    if input_attr != decorator_arg_dict['treat_as']:
                        raise "Error: input type doesn't match"

                if 'whitelist' in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]['whitelist'] = decorator_arg_dict['whitelist']
                elif 'example' in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]['example'] = decorator_arg_dict['example']

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                if decorated_params[function_arg_name]['treat_as'] == 'column':
                    function_arg_type_name = getattr(function_param.annotation.__args__[0], '__name__')
                else:
                    function_arg_type_name = getattr(function_param.annotation, '__name__')
                if function_arg_name not in decorated_params.keys():
                    decorated_params[function_arg_name] = dict()
                decorated_params[function_arg_name]['type'] = function_arg_type_name
            decorated_function = {
                "path": '/call/{}'.format(path),
                "decorated_params": decorated_params,
                "output_type": output_type
            }

            get_wrapper = app.get('/param/{}'.format(path))
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
