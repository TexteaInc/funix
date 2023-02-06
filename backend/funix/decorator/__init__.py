import os
import re
import json
import yaml
import json5
import flask
import inspect
import requests
import traceback
from funix.app import app
from functools import wraps
from typing import Optional
from uuid import uuid4 as uuid
from .theme import parse_theme
from urllib.parse import urlparse
import matplotlib.pyplot as plt, mpld3
from ..hint import DestinationType, WidgetsType, TreatAsType, WhitelistType, ExamplesType, LabelsType, LayoutType, \
    ConditionalVisibleType, ArgumentConfigType

__supported_basic_types_dict = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean"
}
__supported_basic_file_types = ["Images", "Videos", "Audios", "Files"]
__supported_basic_types = list(__supported_basic_types_dict.keys())
__decorated_functions_list = list()
__files_dict = {}
__wrapper_enabled = False
__default_theme = {}
__themes = {}
__parsed_themes = {}

def enable_wrapper():
    global __wrapper_enabled, __files_dict, __decorated_functions_list
    if not __wrapper_enabled:
        __wrapper_enabled = True

        @app.get("/list")
        def __funix_export_func_list():
            return {
                "list": __decorated_functions_list,
            }

        @app.get("/files/<string:fid>")
        def __funix_export_file(fid: str):
            if fid in __files_dict:
                return flask.send_file(__files_dict[fid])
            else:
                return flask.abort(404)

def get_type_dict(annotation):
    if isinstance(annotation, object):  # is class
        annotation_type_class_name = getattr(type(annotation), "__name__")
        if annotation_type_class_name == "_GenericAlias":
            if getattr(annotation, "__module__") == "typing":
                if getattr(annotation, "_name") == "List" or getattr(annotation, "_name") == "Dict":
                    return {
                        "type": str(annotation)
                    }
                elif str(getattr(annotation, "__origin__")) == "typing.Literal":  # Python 3.8
                    literal_first_type = get_type_dict(type(getattr(annotation, "__args__")[0]))["type"]
                    return {
                        "type": literal_first_type,
                        "whitelist": getattr(annotation, "__args__")
                    }
                elif str(getattr(annotation, "__origin__")) == "typing.Union":  # typing.Optional
                    union_first_type = get_type_dict(getattr(annotation, "__args__")[0])["type"]
                    return {
                        "type": union_first_type,
                        "optional": True
                    }
                else:
                    raise Exception("Unsupported typing")
            else:
                raise Exception("Support typing only")
        elif annotation_type_class_name == "_LiteralGenericAlias":  # Python 3.10
            if str(getattr(annotation, "__origin__")) == "typing.Literal":
                literal_first_type = get_type_dict(type(getattr(annotation, "__args__")[0]))["type"]
                return {
                    "type": literal_first_type,
                    "whitelist": getattr(annotation, "__args__")
                }
            else:
                raise Exception("Unsupported annotation")
        elif annotation_type_class_name == "_SpecialGenericAlias":
            if getattr(annotation, "_name") == "Dict" or getattr(annotation, "_name") == "List":
                return {
                    "type": str(annotation)
                }
        elif annotation_type_class_name == "_TypedDictMeta":
            key_and_type = {}
            for key in annotation.__annotations__:
                key_and_type[key] = \
                    __supported_basic_types_dict[annotation.__annotations__[key].__name__] \
                        if annotation.__annotations__[key].__name__ in __supported_basic_types_dict \
                        else annotation.__annotations__[key].__name__
            return {
                "type": "typing.Dict",
                "keys": key_and_type
            }

        elif annotation_type_class_name == "type":
            return {
                "type": getattr(annotation, "__name__")
            }
        else:
            # raise Exception("Unsupported annotation_type_class_name")
            return {
                "type": "typing.Dict"
            }
    else:
        return {
            "type": str(annotation)
        }


def get_type_widget_prop(function_arg_type_name, index, function_arg_widget, widget_type):
    # Basic and List only
    if isinstance(function_arg_widget, str):
        widget = function_arg_widget
    elif isinstance(function_arg_widget, list):
        if index >= len(function_arg_widget):
            widget = ""
        else:
            widget = function_arg_widget[index]
    else:
        widget = ""
    if function_arg_type_name in widget_type:
        widget = widget_type[function_arg_type_name]
    if function_arg_type_name in __supported_basic_types:
        return {
            "type": __supported_basic_types_dict[function_arg_type_name],
            "widget": widget
        }
    elif function_arg_type_name == "list":
        return {
            "type": "array",
            "items": {
              "type": "any",
              "widget": ""
            },
            "widget": widget
        }
    else:
        typing_list_search_result = re.search(
            "typing\.(?P<containerType>List)\[(?P<contentType>.*)]",
            function_arg_type_name)
        if isinstance(typing_list_search_result, re.Match):  # typing.List, typing.Dict
            content_type = typing_list_search_result.group("contentType")
            # (content_type in __supported_basic_types) for yodas only
            return {
                "type": "array",
                "widget": widget,
                "items": get_type_widget_prop(content_type, index + 1, function_arg_widget, widget_type)
            }
        elif function_arg_type_name == "typing.Dict":
            return {
                "type": "object",
                "widget": widget
            }
        elif function_arg_type_name == "typing.List":
            return {
                "type": "array",
                "widget": widget
            }
        else:
            # raise Exception("Unsupported Container Type")
            return {
                "type": "object",
                "widget": widget
            }


def is_valid_uri(uri: str) -> bool:
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def get_static_uri(path: str or list[str]) -> str or list[str]:
    global __files_dict
    if isinstance(path, str):
        if not is_valid_uri(path):
            fid = uuid().hex
            result = f"/files/{fid}"
            abs_path = os.path.abspath(path)
            if not abs_path in list(__files_dict.values()):
                __files_dict[fid] = abs_path
            else:
                return f"/files/{list(__files_dict.keys())[list(__files_dict.values()).index(abs_path)]}"
            return result
        else:
            return path
    else:
        uris = [get_static_uri(uri) for uri in path]
        return uris

def get_theme(path: str):
    if not path:
        return __default_theme
    if is_valid_uri(path):
        return yaml.load(requests.get(path).content, yaml.FullLoader)
    else:
        if path in __themes:
            return __themes[path]
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.load(f.read(), yaml.FullLoader)
        else:
            home_themes_path = os.path.join(os.path.expanduser("~"), os.path.join("./.funix/themes/", path))
            print(home_themes_path)
            if os.path.exists(home_themes_path):
                with open(home_themes_path, "r", encoding="utf-8") as f:
                    return yaml.load(f.read(), yaml.FullLoader)
            else:
                raise Exception(f"Theme {path} not found")


def set_global_theme(path: str):
    global __default_theme, __parsed_themes
    __default_theme = get_theme(path)
    __parsed_themes["__default"] = parse_theme(__default_theme)


def import_theme(path: str, name: str):
    global __themes
    __themes[name] = get_theme(path)

def conv_row_item(row_item: dict, item_type: str):
    conved_item = row_item
    conved_item["type"] = item_type
    conved_item["content"] = row_item[item_type]
    conved_item.pop(item_type)
    return conved_item

def funix(
        path: Optional[str] = None,
        description: Optional[str] = "",
        destination: DestinationType = None,
        theme: Optional[str] = "",
        widgets: WidgetsType = {},
        treat_as: TreatAsType = {},
        whitelist: WhitelistType = {},
        examples: ExamplesType = {},
        argument_labels: LabelsType = {},
        input_layout: LayoutType = [],
        output_layout: LayoutType = [],
        conditional_visible: ConditionalVisibleType = [],
        argument_config: ArgumentConfigType = {}
):
    global __parsed_themes

    def decorator(function: callable):
        if __wrapper_enabled:
            id: str = str(uuid())
            function_name = getattr(function, "__name__")  # function name as id to retrieve function info
            function_theme = get_theme(theme)

            try:
                if theme == "":
                    parsed_theme = __parsed_themes["__default"]
                else:
                    if theme in __parsed_themes:
                        parsed_theme = __parsed_themes[theme]
                    else:
                        parsed_theme = parse_theme(function_theme)
                        __parsed_themes[theme] = parsed_theme
            except:
                parsed_theme = [], {}, {}, {}, {}

            if path is None:
                endpoint = function_name
            else:
                endpoint = path.strip("/")

            __decorated_functions_list.append({
                "name": function_name,
                "path": endpoint
            })

            function_signature = inspect.signature(function)
            function_params = function_signature.parameters
            decorated_params = dict()
            json_schema_props = dict()

            cast_to_list_flag = False
            return_url_not_path_flag = False

            if function_signature.return_annotation is not inspect._empty:
                # return type dict enforcement for yodas only
                try:
                    if cast_to_list_flag := function_signature.return_annotation.__class__.__name__ == "tuple":
                        parsed_return_annotation_list = []
                        return_annotation = list(function_signature.return_annotation)
                        for return_annotation_type in return_annotation:
                            return_annotation_type_name = getattr(return_annotation_type, "__name__")
                            if return_annotation_type_name in __supported_basic_types:
                                return_annotation_type_name = __supported_basic_types_dict[return_annotation_type_name]
                            parsed_return_annotation_list.append(return_annotation_type_name)
                        return_type_parsed = parsed_return_annotation_list
                    else:
                        if hasattr(function_signature.return_annotation, "__annotations__"):
                            return_type_raw = getattr(function_signature.return_annotation, "__annotations__")
                            if getattr(type(return_type_raw), "__name__") == "dict":
                                if getattr(function_signature.return_annotation, "__name__") == "figure":
                                    return_type_parsed = "figure"
                                else:
                                    return_type_parsed = dict()
                                    for return_type_key, return_type_value in return_type_raw.items():
                                        return_type_parsed[return_type_key] = str(return_type_value)
                            else:
                                return_type_parsed = str(return_type_raw)
                        else:
                            return_type_parsed = getattr(function_signature.return_annotation, "__name__")
                            if return_type_parsed in __supported_basic_types:
                                return_type_parsed = __supported_basic_types_dict[return_type_parsed]
                            return_url_not_path_flag = True \
                                if return_type_parsed in __supported_basic_file_types else False
                except:
                    return_type_parsed = get_type_dict(function_signature.return_annotation)["type"]
            else:
                return_type_parsed = None

            return_input_layout = []

            for row in input_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    if "markdown" in row_item:
                        row_item_done = conv_row_item(row_item, "markdown")
                    elif "html" in row_item:
                        row_item_done = conv_row_item(row_item, "html")
                    elif "argument" in row_item:
                        if row_item["argument"] not in decorated_params:
                            decorated_params[row_item["argument"]] = {}
                        decorated_params[row_item["argument"]]["customLayout"] = True
                        row_item_done["type"] = "argument"
                    elif "dividing" in row_item:
                        row_item_done["type"] = "dividing"
                        if isinstance(row_item["dividing"], str):
                            row_item_done["content"] = row_item_done["dividing"]
                        row_item_done.pop("dividing")
                    else:
                        raise Exception("Invalid input layout item")
                    row_layout.append(row_item_done)
                return_input_layout.append(row_layout)

            return_output_layout = []
            return_output_indexs = []

            for row in output_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    if "markdown" in row_item:
                        row_item_done = conv_row_item(row_item, "markdown")
                    elif "html" in row_item:
                        row_item_done = conv_row_item(row_item, "html")
                    elif "dividing" in row_item:
                        row_item_done["type"] = "dividing"
                        if isinstance(row_item["dividing"], str):
                            row_item_done["content"] = row_item_done["dividing"]
                        row_item_done.pop("dividing")
                    elif "images" in row_item:
                        row_item_done = conv_row_item(row_item, "images")
                    elif "videos" in row_item:
                        row_item_done = conv_row_item(row_item, "videos")
                    elif "audios" in row_item:
                        row_item_done = conv_row_item(row_item, "audios")
                    elif "files" in row_item:
                        row_item_done = conv_row_item(row_item, "files")
                    elif "code" in row_item:
                        row_item_done = conv_row_item(row_item, "code")
                    elif "return" in row_item:
                        row_item_done["type"] = "return"
                        return_output_indexs.append(row_item_done["return"])
                    else:
                        raise Exception("Invalid output layout item")
                    row_layout.append(row_item_done)
                return_output_layout.append(row_layout)


            for widget_arg_name in widgets:
                if isinstance(widget_arg_name, str):
                    if widget_arg_name not in decorated_params:
                        decorated_params[widget_arg_name] = {}
                    decorated_params[widget_arg_name]["widget"] = widgets[widget_arg_name]
                else:
                    for widget_arg_name_item in widget_arg_name:
                        if widget_arg_name_item not in decorated_params:
                            decorated_params[widget_arg_name_item] = {}
                        decorated_params[widget_arg_name_item]["widget"] = widgets[widget_arg_name]

            for treat_as_arg_name in treat_as:
                if isinstance(treat_as_arg_name, str):
                    if treat_as_arg_name not in decorated_params:
                        decorated_params[treat_as_arg_name] = {}
                    decorated_params[treat_as_arg_name]["treat_as"] = treat_as[treat_as_arg_name]
                else:
                    for treat_as_arg_name_item in treat_as_arg_name:
                        if treat_as_arg_name_item not in decorated_params:
                            decorated_params[treat_as_arg_name_item] = {}
                        decorated_params[treat_as_arg_name_item]["treat_as"] = treat_as[treat_as_arg_name]

            for example_arg_name in examples:
                if isinstance(example_arg_name, str):
                    if example_arg_name not in decorated_params:
                        decorated_params[example_arg_name] = {}
                    decorated_params[example_arg_name]["example"] = examples[example_arg_name]
                else:
                    example_arg_names = example_arg_name
                    for index, arg_name in enumerate(example_arg_names):
                        if arg_name not in decorated_params:
                            decorated_params[arg_name] = {}
                        decorated_params[arg_name]["example"] = examples[example_arg_name][index]

            for whitelist_arg_name in whitelist:
                if isinstance(whitelist_arg_name, str):
                    if whitelist_arg_name not in decorated_params:
                        decorated_params[whitelist_arg_name] = {}
                    if "example" not in decorated_params[whitelist_arg_name]:
                        decorated_params[whitelist_arg_name]["whitelist"] = whitelist[whitelist_arg_name]
                    else:
                        raise Exception(f"{function_name}: Cannot use whitelist and example together")
                else:
                    whitelist_arg_names = whitelist_arg_name
                    for index, arg_name in enumerate(whitelist_arg_names):
                        if arg_name not in decorated_params:
                            decorated_params[arg_name] = {}
                        if "example" not in decorated_params[arg_name]:
                            decorated_params[arg_name]["whitelist"] = whitelist[whitelist_arg_name][index]
                        else:
                            raise Exception(f"{function_name}: Cannot use whitelist and example together")

            for label_arg_name in argument_labels:
                if isinstance(label_arg_name, str):
                    if label_arg_name not in decorated_params:
                        decorated_params[label_arg_name] = {}
                    decorated_params[label_arg_name]["label"] = argument_labels[label_arg_name]
                else:
                    label_arg_names = label_arg_name
                    for arg_name in label_arg_names:
                        if arg_name not in decorated_params:
                            decorated_params[arg_name] = {}
                        decorated_params[arg_name]["label"] = argument_labels[label_arg_name]

            input_attr = ""
            for decorator_arg_name, decorator_arg_dict in argument_config.items():
                if decorator_arg_name not in decorated_params.keys():
                    decorated_params[decorator_arg_name] = dict()

                if decorator_arg_dict["treat_as"] == "config":
                    decorated_params[decorator_arg_name]["treat_as"] = "config"
                else:
                    decorated_params[decorator_arg_name]["treat_as"] = decorator_arg_dict["treat_as"]
                    input_attr = decorator_arg_dict["treat_as"] if input_attr == "" else input_attr
                    if input_attr != decorator_arg_dict["treat_as"]:
                        raise Exception("Error: input type doesn't match")

                if "widget" in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]["widget"] = decorator_arg_dict["widget"]

                if "label" in decorator_arg_dict.keys():
                    decorated_params[decorator_arg_name]["label"] = decorator_arg_dict["label"]

                if "whitelist" in decorator_arg_dict.keys():
                    if "example" in decorated_params[decorator_arg_name]:
                        raise Exception(f"{function_name}: Cannot use whitelist and example together")
                    decorated_params[decorator_arg_name]["whitelist"] = decorator_arg_dict["whitelist"]
                elif "example" in decorator_arg_dict.keys():
                    if "whitelist" in decorated_params[decorator_arg_name]:
                        raise Exception(f"{function_name}: Cannot use whitelist and example together")
                    decorated_params[decorator_arg_name]["example"] = decorator_arg_dict["example"]

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                if function_arg_name not in decorated_params.keys():
                    decorated_params[function_arg_name] = dict()  # default

                if "treat_as" not in decorated_params[function_arg_name].keys():
                    decorated_params[function_arg_name]["treat_as"] = "config"  # default
                function_arg_type_dict = get_type_dict(function_param.annotation)
                if function_arg_name not in decorated_params.keys():
                    decorated_params[function_arg_name] = dict()
                decorated_params[function_arg_name].update(function_arg_type_dict)

                default_example = function_param.default
                if not default_example is inspect._empty:
                    decorated_params[function_arg_name]["default"] = default_example
                elif decorated_params[function_arg_name]["type"] == "bool":
                    decorated_params[function_arg_name]["default"] = False
                elif "optional" in decorated_params[function_arg_name].keys() and \
                        decorated_params[function_arg_name]["optional"]:
                    decorated_params[function_arg_name]["default"] = None
                if function_arg_name not in json_schema_props.keys():
                    json_schema_props[function_arg_name] = dict()
                if "widget" in decorated_params[function_arg_name].keys():
                    widget = decorated_params[function_arg_name]["widget"]
                else:
                    if function_arg_type_dict["type"] in ["list", "dict", "typing.Dict"]:
                        widget = "json"
                    else:
                        widget = ""
                json_schema_props[function_arg_name] = get_type_widget_prop(
                    function_arg_type_dict["type"],
                    0,
                    widget,
                    parsed_theme[1]
                )
                if "whitelist" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["whitelist"] = decorated_params[function_arg_name]["whitelist"]
                elif "example" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["example"] = decorated_params[function_arg_name]["example"]
                elif "keys" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["keys"] = decorated_params[function_arg_name]["keys"]
                if "default" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["default"] = decorated_params[function_arg_name]["default"]
                if "label" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["title"] = decorated_params[function_arg_name]["label"]
                if "customLayout" in decorated_params[function_arg_name].keys():
                    json_schema_props[function_arg_name]["customLayout"] = decorated_params[function_arg_name][
                        "customLayout"]
                else:
                    json_schema_props[function_arg_name]["customLayout"] = False

                if decorated_params[function_arg_name]["treat_as"] == "cell":
                    return_type_parsed = "array"
                    json_schema_props[function_arg_name]["items"] = \
                        get_type_widget_prop(function_arg_type_dict["type"], 0, widget[1:], {})
                    json_schema_props[function_arg_name]["type"] = "array"

            all_of = []

            for conditional_visible_item in conditional_visible:
                config = {
                    "if": {
                        "properties": {}
                    },
                    "then": {
                        "properties": {}
                    },
                    "required": []
                }
                if_items = conditional_visible_item["if"]
                then_items = conditional_visible_item["then"]
                for if_item in if_items.keys():
                    config["if"]["properties"][if_item] = {
                        "const": if_items[if_item]
                    }
                for then_item in then_items:
                    config["then"]["properties"][then_item] = json_schema_props[then_item]
                    config["required"].append(then_item)
                    json_schema_props.pop(then_item)
                all_of.append(config)

            keep_ordered_list = list(function_signature.parameters.keys())
            keep_ordered_dict = {}
            for key in keep_ordered_list:
                if key in json_schema_props.keys():
                    keep_ordered_dict[key] = json_schema_props[key]

            decorated_function = {
                "id": id,
                "name": function_name,
                "params": decorated_params,
                "theme": parsed_theme[4],
                "return_type": return_type_parsed,
                "description": description,
                "schema": {
                    "title": function_name,
                    "description": description,
                    "type": "object",
                    "properties": keep_ordered_dict,
                    "allOf": all_of,
                    "input_layout": return_input_layout,
                    "output_layout": return_output_layout,
                    "output_indexs": return_output_indexs
                },
                "destination": destination
            }

            get_wrapper = app.get(f"/param/{endpoint}")

            def decorated_function_param_getter():
                return flask.Response(json.dumps(decorated_function), mimetype="application/json")

            decorated_function_param_getter.__setattr__("__name__", f"{function_name}_param_getter")
            get_wrapper(decorated_function_param_getter)

            @wraps(function)
            def wrapper():
                try:
                    function_kwargs = flask.request.get_json()

                    @wraps(function)
                    def wrapped_function(**wrapped_function_kwargs):
                        try:
                            if return_type_parsed == "figure":
                                fig = function(**wrapped_function_kwargs)
                                fig_dict = mpld3.fig_to_dict(fig)
                                fig_dict["width"] = 560
                                return fig_dict
                            else:
                                result = function(**wrapped_function_kwargs)
                                if not isinstance(result, (str, dict, tuple)):
                                    result = str(result)
                                if cast_to_list_flag:
                                    result = list(result)
                                    for index, single_return_type in enumerate(return_type_parsed):
                                        if single_return_type == "figure":
                                            fig_dict = mpld3.fig_to_dict(result[index])
                                            fig_dict["width"] = 560
                                            result[index] = fig_dict
                                        if single_return_type in __supported_basic_file_types:
                                            if type(result[index]) == "list":
                                                result[index] = [get_static_uri(each) for each in result[index]]
                                            else:
                                                result[index] = get_static_uri(result[index])
                                    return result
                                if return_url_not_path_flag:
                                    result[index] = get_static_uri(result[index])
                                return result
                        except:
                            return {
                                "error_type": "function",
                                "error_body": traceback.format_exc()
                            }

                    cell_names = []
                    for key in decorated_params.keys():
                        if decorated_params[key]["treat_as"] == "cell":
                            cell_names.append(key)
                    if len(cell_names) > 0:
                        length = len(function_kwargs[cell_names[0]])
                        static_keys = function_kwargs.keys() - cell_names
                        result = []
                        for i in range(length):
                            arg = {}
                            for cell_name in cell_names:
                                arg[cell_name] = function_kwargs[cell_name][i]
                            for static_key in static_keys:
                                arg[static_key] = function_kwargs[static_key]
                            result.append(wrapped_function(**arg))
                        return {"result": result}
                    else:
                        return wrapped_function(**function_kwargs)
                except:
                    return {
                        "error_type": "wrapper",
                        "error_body": traceback.format_exc()
                    }

            post_wrapper = app.post(f"/call/{id}")
            post_wrapper(wrapper)
            post_wrapper = app.post(f"/call/{endpoint}")
            post_wrapper(wrapper)
            wrapper._decorator_name_ = "funix"
        return function

    return decorator

def funix_json(config: Optional[str] = ""):
    def decorator(function: callable):
        if config == "":
            return funix()(function)
        jsonConfig = json5.loads(config)
        return funix(**jsonConfig)(function)

    return decorator

def funix_yaml(config: Optional[str] = ""):
    def decorator(function: callable):
        if config == "":
            return funix()(function)
        yamlConfig = yaml.load(config, Loader=yaml.FullLoader)
        return funix(**yamlConfig)(function)

    return decorator
