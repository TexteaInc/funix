import inspect
import json
from functools import wraps

import flask

from app import app

supported_basic_types = ['int', 'float', 'str']


def TexteaExport(path: str, **decorator_kwargs):
    def decorator(function: callable):
        print(decorator_kwargs)
        post_wrapper = app.post(path)

        @wraps(function)
        async def wrapper():
            params = inspect.signature(function).parameters
            request_kwargs = flask.request.form
            function_kwargs = dict()
            for (k, v) in request_kwargs.items():
                arg_type = params[k].annotation
                arg_type_name = getattr(arg_type, '__name__')
                if k in params.keys():
                    if arg_type_name in supported_basic_types:
                        function_kwargs[k] = arg_type(v)
                    elif arg_type_name == 'dict' or arg_type_name == 'list':
                        function_kwargs[k] = json.loads(v)
                    else:
                        raise 'Not supported'
            wrapped_function = function(**function_kwargs)
            return wrapped_function

        wrapper._decorator_name_ = 'TexteaExport'
        post_wrapper(wrapper)
        return wrapper

    return decorator
