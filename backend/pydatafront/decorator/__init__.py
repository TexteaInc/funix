import builtins
import inspect
import json
import re
import traceback
from functools import wraps
from typing import Literal
from uuid import uuid4 as uuid

import flask

from pydatafront import app

__supported_basic_types = ["int", "float", "str", "bool"]
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


def get_type_dict(annotation):
    if isinstance(annotation, object):  # is class
        annotation_type_class_name = getattr(type(annotation), "__name__")
        if annotation_type_class_name == "_GenericAlias":
            if getattr(annotation, "__module__") == "typing":
                if getattr(annotation, "_name") == "List":
                    return {
                        "type": str(annotation)
                    }
                elif str(getattr(annotation, "__origin__")) == "typing.Literal":
                    literal_first_type = get_type_dict(type(getattr(annotation, "__args__")[0]))["type"]
                    return {
                        "type": literal_first_type,
                        "whitelist": getattr(annotation, "__args__")
                    }
                elif str(getattr(annotation, "__origin__")) == "typing.Union":
                    union_first_type = get_type_dict(getattr(annotation, "__args__")[0])["type"]
                    return {
                        "type": union_first_type
                    }
                else:
                    raise "Unsupported typing"
            else:
                raise "Support typing only"
        elif annotation_type_class_name == "type":
            return {
                "type": getattr(annotation, "__name__")
            }
    else:
        return {
            "type": str(annotation)
        }


def get_type_prop(function_arg_type_name):
    # Basic and List only
    if function_arg_type_name in __supported_basic_types:
        if function_arg_type_name == "int":
            return {
                "type": "integer"
            }
        elif function_arg_type_name == "bool":
            return {
                "type": "boolean"
            }
        elif function_arg_type_name == "float":
            return {
                "type": "number"
            }
        elif function_arg_type_name == "str":
            return {
                "type": "string"
            }
        else:
            raise "Unsupported Basic Type"
    elif function_arg_type_name == "list":
        return {
            "type": "array"
        }
    else:
        typing_list_search_result = re.search(
            "typing\.(?P<containerType>List)\[(?P<contentType>.*)]",
            function_arg_type_name)
        if isinstance(typing_list_search_result, re.Match):  # typing.List, typing.Dict
            content_type = typing_list_search_result.group("contentType")
            if content_type in __supported_basic_types:
                return {
                    "type": "array",
                    "items": get_type_prop(content_type)
                }
            else:
                raise "Unsupported Content Type"
        else:
            raise "Unsupported Container Type"


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


def textea_export(path: str, description: str = "", destination: Literal["column", "row", "sheet"] = None,
                  **decorator_kwargs):
    def decorator(function: callable):
        if __wrapper_enabled:
            id: str = str(uuid())
            function_name = getattr(function, "__name__")  # function name as id to retrieve function info
            __decorated_functions_list.append({
                "id": id,
                "name": function_name
            })

            function_signature = inspect.signature(function)
            function_params = function_signature.parameters
            decorated_params = dict()
            json_schema_props = dict()

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
                    # deprecated, for compatibility
                    decorated_params[decorator_arg_name]["whitelist"] = decorator_arg_dict["whitelist"]
                elif "example" in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]["example"] = decorator_arg_dict["example"]

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                if decorated_params[function_arg_name]["treat_as"] == "cell":
                    raise "Don't use cell!"
                else:
                    function_arg_type_dict = get_type_dict(function_param.annotation)
                if function_arg_name not in decorated_params.keys():
                    decorated_params[function_arg_name] = dict()
                decorated_params[function_arg_name].update(function_arg_type_dict)
                default_example = function_param.default
                if default_example is not inspect.Parameter.empty:
                    if "example" in decorated_params[function_arg_name].keys():
                        decorated_params[function_arg_name].get("example").append(default_example)
                    else:
                        decorated_params[function_arg_name]["example"] = [
                            default_example
                        ]

                if function_arg_name not in json_schema_props.keys():
                    json_schema_props[function_arg_name] = dict()
                json_schema_props[function_arg_name] = get_type_prop(function_arg_type_dict["type"])
                if json_schema_props[function_arg_name]["type"] != "array":
                    # support (treat_as == config) only
                    if "whitelist" in decorated_params[function_arg_name].keys():
                        json_schema_props[function_arg_name]["whitelist"] = decorated_params[function_arg_name][
                            "whitelist"]
                    elif "example" in decorated_params[function_arg_name].keys():
                        json_schema_props[function_arg_name]["example"] = decorated_params[function_arg_name]["example"]

            decorated_function = {
                "id": id,
                "name": function_name,
                "callee": "/call/{}".format(path),
                "params": decorated_params,
                "output_type": output_type_parsed,
                "description": description,
                "schema": {
                    "title": function_name,
                    "description": description,
                    "type": "object",
                    "properties": json_schema_props
                },
                "destination": destination
            }

            get_wrapper = app.get("/param/{}".format(id))

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
                                function_arg_type_name = get_type_dict(function_arg_type)
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
