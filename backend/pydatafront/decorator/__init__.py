import builtins
import inspect
import json
import re
import traceback
from uuid import uuid4 as uuid
from functools import wraps

import flask

from pydatafront import app

__supported_basic_types = ["int", "float", "str"]
__supported_types = __supported_basic_types + ["dict", "list"]
__decorated_functions_list = list()
__wrapper_enabled = False


def enable_wrapper():
    global __wrapper_enabled
    if not __wrapper_enabled:
        __wrapper_enabled = True

        @app.get("/list")
        def __textea_export_func_list():
            return {
                "list": __decorated_functions_list,
            }


def get_type_name(annotation):
    if isinstance(annotation, object):  # is class
        annotation_type_class_name = getattr(type(annotation), "__name__")
        if annotation_type_class_name == "_GenericAlias":
            return str(annotation)
        elif annotation_type_class_name == "type":
            return getattr(annotation, "__name__")
    else:
        return str(annotation)


def extract_request_arg(function_arg_type_name, request_arg):
    if function_arg_type_name in __supported_basic_types:
        converter = getattr(builtins, function_arg_type_name)
        return converter(request_arg)
    elif function_arg_type_name == "dict" or function_arg_type_name == "list":
        return json.loads(request_arg)
    else:
        typing_container_search_result = re.search(
            "typing\.(?P<containerType>List|Dict)\[(?P<contentType>.*)]",
            function_arg_type_name)
        typing_union_search_result = re.search(
            "typing\.Union\[(?P<unionTypes>.*)]",
            function_arg_type_name)
        if isinstance(typing_container_search_result, re.Match):  # typing.List, typing.Dict
            content_type = typing_container_search_result.group("contentType")
            if content_type in __supported_basic_types:
                return json.loads(request_arg)
        elif isinstance(typing_union_search_result, re.Match):  # typing.Union (for typing.Optional only)
            union_types_raw = typing_union_search_result.group("unionTypes")
            union_types = union_types_raw.split(", ")
            if (request_arg is None or request_arg == "") and "NoneType" in union_types:
                return None
            else:
                union_types.remove("NoneType")
            if len(union_types) == 1:
                return extract_request_arg(union_types[0], request_arg)
        raise "Unsupported type"


def textea_export(path: str, description: str = "", **decorator_kwargs):
    def decorator(function: callable):
        if __wrapper_enabled:
            id: str = str(uuid())
            function_name = getattr(function, "__name__")  # function name as id to retrieve function info
            __decorated_functions_list.append({
                "id": id,
                "name": function_name,
                "path": "/param/{}".format(path),
                "description": description
            })

            function_signature = inspect.signature(function)
            function_params = function_signature.parameters
            decorated_params = dict()

            output_type_raw = getattr(function_signature.return_annotation, "__annotations__")
            if getattr(type(output_type_raw), "__name__") == "dict":
                output_type_parsed = dict()
                for output_type_key, output_type_value in output_type_raw.items():
                    output_type_parsed[output_type_key] = str(output_type_value)
            else:
                output_type_parsed = output_type_raw

            input_attr = ""
            for decorator_arg_name, decorator_arg_dict in decorator_kwargs.items():
                if decorator_arg_name not in decorated_params.keys():
                    decorated_params[decorator_arg_name] = dict()
                if decorator_arg_dict["treat_as"] == "config":
                    decorated_params[decorator_arg_name]["treat_as"] = "config"
                else:
                    decorated_params[decorator_arg_name]["treat_as"] = decorator_arg_dict["treat_as"]
                    input_attr = decorator_arg_dict["treat_as"] if input_attr == "" else input_attr
                    if input_attr != decorator_arg_dict["treat_as"]:
                        raise "Error: input type doesn't match"

                if "whitelist" in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]["whitelist"] = decorator_arg_dict["whitelist"]
                elif "example" in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]["example"] = decorator_arg_dict["example"]

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                if decorated_params[function_arg_name]["treat_as"] == "cell":
                    raise "Don't use cell!"
                else:
                    function_arg_type_name = get_type_name(function_param.annotation)
                if function_arg_name not in decorated_params.keys():
                    decorated_params[function_arg_name] = dict()
                decorated_params[function_arg_name]["type"] = function_arg_type_name

            decorated_function = {
                "id": id,
                "name": function_name,
                "callee": "/call/{}".format(path),
                "params": decorated_params,
                "output_type": output_type_parsed,
                "description": description
            }

            get_wrapper = app.get("/param/{}".format(path))

            def decorated_function_param_getter():
                return decorated_function

            decorated_function_param_getter.__setattr__("__name__", "{}_param_getter".format(function_name))
            get_wrapper(decorated_function_param_getter)

            @wraps(function)
            def wrapper():
                try:
                    if flask.request.content_type.startswith("application/json"):
                        request_kwargs = flask.request.get_json()
                    else:
                        # deprecated
                        request_kwargs = flask.request.form

                    if request_kwargs.get("__textea_sheet", False):
                        # for textea-sheet
                        del request_kwargs["__textea_sheet"]
                        function_kwargs = request_kwargs
                    else:
                        function_kwargs = dict()
                        for request_arg_name, request_arg in request_kwargs.items():
                            if request_arg_name in function_params.keys():
                                function_arg_type = function_params[request_arg_name].annotation
                                function_arg_type_name = get_type_name(function_arg_type)
                                extracted_request_arg = extract_request_arg(function_arg_type_name, request_arg)
                                if extracted_request_arg is not None:
                                    function_kwargs[request_arg_name] = extracted_request_arg

                    @wraps(function)
                    def wrapped_function(**wrapped_function_kwargs):
                        try:
                            result = function(**wrapped_function_kwargs)
                            if not isinstance(result, (str, dict, tuple)):
                                result = str(result)
                            return result
                        except:
                            return {
                                "error_type": "function",
                                "error_body": traceback.format_exc()
                            }

                    return wrapped_function(**function_kwargs)
                except:
                    return {
                        "error_type": "wrapper",
                        "error_body": traceback.format_exc()
                    }

            post_wrapper = app.post("/call/{}".format(path))
            post_wrapper(wrapper)
            wrapper._decorator_name_ = "textea_export"
        return function

    return decorator
