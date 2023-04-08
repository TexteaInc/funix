import io
import os
import re
import json
import yaml
import json5
import flask
import inspect
import secrets
import requests
import traceback
import matplotlib
from funix.app import app
from functools import wraps
from uuid import uuid4 as uuid
from .theme import parse_theme
from urllib.parse import urlparse
from urllib.request import urlopen
import matplotlib.pyplot as plt, mpld3
from typing import Literal, Optional, Callable, Any
from ..widget import generate_frontend_widget_config
from ..hint import DestinationType, WidgetsType, TreatAsType, WhitelistType, ExamplesType, LabelsType, LayoutType, \
    ConditionalVisibleType, ArgumentConfigType

__supported_basic_types_dict = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean"
}
__supported_basic_file_types = ["Images", "Videos", "Audios", "Files"]
__supported_upload_widgets = ["image", "video", "audio", "file"]
__banned_function_name_and_path = ["list", "file", "static", "config", "param", "call"]
__supported_basic_types = list(__supported_basic_types_dict.keys())
__decorated_functions_list = []
__decorated_functions_names_list = []
__decorated_secret_functions_dict = {}
__decorated_id_to_function_dict = {}
__files_dict = {}
__wrapper_enabled = False
__default_theme = {}
__themes = {}
__parsed_themes = {}

matplotlib.use("Agg")

def enable_wrapper():
    global __wrapper_enabled, __files_dict, __decorated_functions_list
    if not __wrapper_enabled:
        __wrapper_enabled = True

        @app.get("/list")
        def __funix_export_func_list():
            return {
                "list": __decorated_functions_list,
            }

        @app.get("/file/<string:fid>")
        def __funix_export_file(fid: str):
            if fid in __files_dict:
                if isinstance(__files_dict[fid], str):
                    return flask.send_file(__files_dict[fid])
                else:
                    return flask.send_file(io.BytesIO(__files_dict[fid]), mimetype="application/octet-stream")
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
                    literal_first_type = get_type_dict(type(getattr(annotation, "__args__")[0]))
                    if literal_first_type is None:
                        raise Exception("Unsupported typing")
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
        elif annotation_type_class_name == "range":
            return {
                "type": "range"
            }
        elif annotation_type_class_name in ["UnionType", "_UnionGenericAlias"]:
            if len(getattr(annotation, "__args__")) != 2 or \
                getattr(annotation, "__args__")[0].__name__ == "NoneType" or \
                getattr(annotation, "__args__")[1].__name__ != "NoneType":
                raise Exception("Must be X | None, Optional[X] or Union[X, None]")
            return get_type_dict(getattr(annotation, "__args__")[0])
        else:
            # raise Exception("Unsupported annotation_type_class_name")
            return {
                "type": "typing.Dict"
            }
    else:
        return {
            "type": str(annotation)
        }


def get_type_widget_prop(function_arg_type_name, index, function_arg_widget, widget_type, function_annotation):
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
    for single_widget_type in widget_type:
        if function_annotation.__name__ == single_widget_type:
            widget = widget_type[single_widget_type]
            break
    if function_arg_type_name in __supported_basic_types:
        return {
            "type": __supported_basic_types_dict[function_arg_type_name],
            "widget": widget
        }
    elif function_arg_type_name.startswith("range"):
        return {
            "type": "integer",
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
            r"typing\.(?P<containerType>List)\[(?P<contentType>.*)]",
            function_arg_type_name)
        if isinstance(typing_list_search_result, re.Match):  # typing.List, typing.Dict
            content_type = typing_list_search_result.group("contentType")
            # (content_type in __supported_basic_types) for yodas only
            return {
                "type": "array",
                "widget": widget,
                "items": get_type_widget_prop(
                    content_type,
                    index + 1,
                    function_arg_widget,
                    widget_type,
                    function_annotation
                )
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

def get_real_uri(path: str | bytes) -> str:
    if isinstance(path, bytes):
        fid = uuid().hex
        result = f"/file/{fid}"
        if not path in list(__files_dict.values()):
            __files_dict[fid] = path
        else:
            return f"/file/{list(__files_dict.keys())[list(__files_dict.values()).index(path)]}"
        return result
    if not is_valid_uri(path):
        fid = uuid().hex + "." + path.split(".")[-1]
        result = f"/file/{fid}"
        abs_path = os.path.abspath(path)
        if not abs_path in list(__files_dict.values()):
            __files_dict[fid] = abs_path
        else:
            return f"/file/{list(__files_dict.keys())[list(__files_dict.values()).index(abs_path)]}"
        return result
    else:
        return path

def get_static_uri(path: str | list[str] | bytes | list[bytes]) -> str | list[str]:
    global __files_dict
    if isinstance(path, (str, bytes)):
        return get_real_uri(path)
    elif isinstance(path, list):
        uris = [get_real_uri(uri) for uri in path]
        return uris
    else:
        raise Exception("Unsupported path type")


def get_theme(path: str | None) -> Any:
    if path is None:
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
            if os.path.exists(home_themes_path):
                with open(home_themes_path, "r", encoding="utf-8") as f:
                    return yaml.load(f.read(), yaml.FullLoader)
            else:
                raise Exception(f"Theme {path} not found")


def set_default_theme(path: str):
    global __default_theme, __parsed_themes
    __default_theme = get_theme(path)
    __parsed_themes["__default"] = parse_theme(__default_theme)

def import_theme(path: str, name: str):
    global __themes
    __themes[name] = get_theme(path)

def set_theme(theme: dict, name: Optional[str] = None):
    global __themes
    if name is None:
        if "name" in theme:
            name = theme["name"]
        else:
            raise Exception("Theme name not found")
    __themes[name] = theme

def set_theme_parser_backend(theme: str, name: Optional[str] = None, parser: Literal["json5", "yaml"] = "json5"):
    global __themes
    if parser == "json5":
        set_theme(json5.loads(theme), name)
    elif parser == "yaml":
        set_theme(yaml.load(theme, yaml.FullLoader), name)
    else:
        raise ValueError(f"Unknown parser: {parser}")

def clear_default_theme():
    global __default_theme, __parsed_themes
    __default_theme = {}
    __parsed_themes.pop("__default")

def set_theme_yaml(theme: str, name: Optional[str] = None):
    set_theme_parser_backend(theme, name, "yaml")

def set_theme_json5(theme: str, name: Optional[str] = None):
    set_theme_parser_backend(theme, name, "json5")

def conv_row_item(row_item: dict, item_type: str):
    conved_item = row_item
    conved_item["type"] = item_type
    conved_item["content"] = row_item[item_type]
    conved_item.pop(item_type)
    return conved_item

def funix_param_to_widget(annotation):
    need_config = hasattr(annotation, "__funix_config__")
    if need_config:
        return f"{annotation.__funix_widget__}{json.dumps(list(annotation.__funix_config__.values()))}"
    else:
        return annotation.__funix_widget__

def function_param_to_widget(annotation, widget):
    if type(annotation) is range or annotation is range:
        start = annotation.start if type(annotation.start) is int else 0
        stop = annotation.stop if type(annotation.stop) is int else 101
        step = annotation.step if type(annotation.step) is int else 1
        widget = f"slider[{start},{stop - 1},{step}]"
    elif hasattr(annotation, "__funix__"):
        widget = funix_param_to_widget(annotation)
    else:
        if type(annotation).__name__ == "_GenericAlias" and annotation.__name__ == "List":
            if annotation.__args__[0] is range or type(annotation.__args__[0]) is range:
                arg = annotation.__args__[0]
                start = arg.start if type(arg.start) is int else 0
                stop = arg.stop if type(arg.stop) is int else 101
                step = arg.step if type(arg.step) is int else 1
                widget = [widget if isinstance(widget, str) else widget[0],
                          f"slider[{start},{stop - 1},{step}]"]
            elif hasattr(annotation.__args__[0], "__funix__"):
                widget = [widget if isinstance(widget, str) else widget[0],
                          funix_param_to_widget(annotation.__args__[0])]
    return widget


def funix(
        path: Optional[str] = None,
        title: Optional[str] = None,
        secret: bool = False,
        description: Optional[str] = "",
        destination: DestinationType = None,
        show_source: bool = False,
        theme: Optional[str] = None,
        widgets: WidgetsType = {},
        treat_as: TreatAsType = {},
        whitelist: WhitelistType = {},
        examples: ExamplesType = {},
        argument_labels: LabelsType = {},
        input_layout: LayoutType = [],
        output_layout: LayoutType = [],
        conditional_visible: ConditionalVisibleType = [],
        argument_config: ArgumentConfigType = {},
        __full_module: Optional[str] = None,
):
    global __parsed_themes

    def decorator(function: Callable):
        if __wrapper_enabled:
            id: str = str(uuid())
            function_name = getattr(function, "__name__")  # function name as id to retrieve function info
            if function_name in __banned_function_name_and_path:
                raise Exception(f"{function_name} is not allowed, banned names: {__banned_function_name_and_path}")
            function_theme = get_theme(theme)
            function_title = title if title is not None else function_name

            try:
                if theme is None or theme == "":
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
                if path in __banned_function_name_and_path:
                    raise Exception(f"{function_name}'s path: {path} is not allowed")
                endpoint = path.strip("/")

            if function_title in __decorated_functions_names_list:
                raise Exception(f"Function with name {function_title} already exists")

            if secret:
                __decorated_id_to_function_dict[id] = function_title
                __decorated_secret_functions_dict[id] = secrets.token_hex(16)

            __decorated_functions_names_list.append(function_title)
            __decorated_functions_list.append({
                "name": function_title,
                "path": endpoint,
                "module": __full_module,
                "secret": secret,
            })

            if show_source:
                source_code = inspect.getsource(function)
            else:
                source_code = ""

            function_signature = inspect.signature(function)
            function_params = function_signature.parameters
            decorated_params = {}
            json_schema_props = {}

            cast_to_list_flag = False

            if function_signature.return_annotation is not inspect._empty:
                # return type dict enforcement for yodas only
                try:
                    if cast_to_list_flag := function_signature.return_annotation.__class__.__name__ == "tuple" or \
                         function_signature.return_annotation.__name__ == "Tuple":
                        parsed_return_annotation_list = []
                        return_annotation = list(
                            function_signature.return_annotation
                            if function_signature.return_annotation.__class__.__name__ == "tuple" else
                            function_signature.return_annotation.__args__
                        )
                        for return_annotation_type in return_annotation:
                            return_annotation_type_name = getattr(return_annotation_type, "__name__")
                            if return_annotation_type_name in __supported_basic_types:
                                return_annotation_type_name = __supported_basic_types_dict[return_annotation_type_name]
                            elif return_annotation_type_name == "List":
                                list_type_name = getattr(getattr(return_annotation_type, "__args__")[0], "__name__")
                                if list_type_name in __supported_basic_file_types:
                                    return_annotation_type_name = list_type_name
                            parsed_return_annotation_list.append(return_annotation_type_name)
                        return_type_parsed = parsed_return_annotation_list
                    else:
                        if hasattr(function_signature.return_annotation, "__annotations__"):
                            return_type_raw = getattr(function_signature.return_annotation, "__annotations__")
                            if getattr(type(return_type_raw), "__name__") == "dict":
                                if function_signature.return_annotation.__name__ == "Figure":
                                    return_type_parsed = "Figure"
                                else:
                                    return_type_parsed = {}
                                    for return_type_key, return_type_value in return_type_raw.items():
                                        return_type_parsed[return_type_key] = str(return_type_value)
                            else:
                                return_type_parsed = str(return_type_raw)
                        else:
                            return_type_parsed = getattr(function_signature.return_annotation, "__name__")
                            if return_type_parsed in __supported_basic_types:
                                return_type_parsed = __supported_basic_types_dict[return_type_parsed]
                            elif return_type_parsed == "List":
                                list_type_name = getattr(getattr(function_signature.return_annotation, "__args__")[0], "__name__")
                                if list_type_name in __supported_basic_file_types:
                                    return_type_parsed = list_type_name
                except:
                    return_type_parsed = get_type_dict(function_signature.return_annotation)
                    if not return_type_parsed is None:
                        return_type_parsed = return_type_parsed["type"]
            else:
                return_type_parsed = None

            return_input_layout = []

            safe_input_layout = [] if input_layout is None else input_layout

            for row in safe_input_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    for common_row_item_key in ["markdown", "html"]:
                        if common_row_item_key in row_item:
                            row_item_done = conv_row_item(row_item, common_row_item_key)
                    if "argument" in row_item:
                        if row_item["argument"] not in decorated_params:
                            decorated_params[row_item["argument"]] = {}
                        decorated_params[row_item["argument"]]["customLayout"] = True
                        row_item_done["type"] = "argument"
                    elif "dividing" in row_item:
                        row_item_done["type"] = "dividing"
                        if isinstance(row_item["dividing"], str):
                            row_item_done["content"] = row_item_done["dividing"]
                        row_item_done.pop("dividing")
                    row_layout.append(row_item_done)
                return_input_layout.append(row_layout)

            return_output_layout = []
            return_output_indexes = []

            safe_output_layout = [] if output_layout is None else output_layout

            for row in safe_output_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    for common_row_item_key in ["markdown", "html", "images", "videos", "audios", "files"]:
                        if common_row_item_key in row_item:
                            row_item_done = conv_row_item(row_item, common_row_item_key)
                    if "dividing" in row_item:
                        row_item_done["type"] = "dividing"
                        if isinstance(row_item["dividing"], str):
                            row_item_done["content"] = row_item_done["dividing"]
                        row_item_done.pop("dividing")
                    elif "code" in row_item:
                        row_item_done = row_item
                        row_item_done["type"] = "code"
                        row_item_done["content"] = row_item_done["code"]
                        row_item_done.pop("code")
                    elif "return" in row_item:
                        row_item_done["type"] = "return"
                        return_output_indexes.append(row_item_done["return"])
                    row_layout.append(row_item_done)
                return_output_layout.append(row_layout)


            def create_decorated_params(arg_name: str):
                if arg_name not in decorated_params:
                    decorated_params[arg_name] = {}

            def put_props_in_params(arg_name: str, prop_name: str, prop_value: any):
                create_decorated_params(arg_name)
                decorated_params[arg_name][prop_name] = prop_value

            def check_example_whitelist(arg_name: str):
                if arg_name in decorated_params:
                    if "example" in decorated_params[arg_name] and "whitelist" in decorated_params[arg_name]:
                        raise Exception(f"{function_name}: {arg_name} has both an example and a whitelist")

            def parse_widget(widget: str | tuple | list):
                if isinstance(widget, str):
                    return widget
                elif isinstance(widget, tuple):
                    return generate_frontend_widget_config(widget)
                elif isinstance(widget, list):
                    result = []
                    for widget_item in widget:
                        if isinstance(widget_item, tuple):
                            result.append(generate_frontend_widget_config(widget_item))
                        elif isinstance(widget_item, list):
                            result.append(parse_widget(widget_item))
                        elif isinstance(widget_item, str):
                            result.append(widget_item)
                    return result

            safe_widgets = {} if widgets is None else widgets
            safe_treat_as = {} if treat_as is None else treat_as
            safe_examples = {} if examples is None else examples
            safe_whitelist = {} if whitelist is None else whitelist
            safe_argument_labels = {} if argument_labels is None else argument_labels

            for prop in [
                (safe_widgets, "widget"),
                (safe_treat_as, "treat_as"),
                (safe_argument_labels, "title"),
                (safe_examples, "example"),
                (safe_whitelist, "whitelist")
            ]:
                for prop_arg_name in prop[0]:
                    if isinstance(prop_arg_name, str):
                        if prop[1] == "widget":
                            put_props_in_params(prop_arg_name, prop[1], parse_widget(prop[0][prop_arg_name]))
                        else:
                            put_props_in_params(prop_arg_name, prop[1], prop[0][prop_arg_name])
                        if prop[1] in ["example", "whitelist"]:
                            check_example_whitelist(prop_arg_name)
                    else:
                        if prop[1] in ["example", "whitelist"]:
                            for index, prop_arg_name in enumerate(prop_arg_name):
                                put_props_in_params(prop_arg_name, prop[1], prop[0][prop_arg_name][index])
                                check_example_whitelist(prop_arg_name)
                        elif prop[1] == "widget":
                            cached_result = parse_widget(prop[0][prop_arg_name])
                            for prop_arg_name_item in prop_arg_name:
                                put_props_in_params(prop_arg_name_item, prop[1], cached_result)
                        else:
                            for prop_arg_name_item in prop_arg_name:
                                put_props_in_params(prop_arg_name_item, prop[1], prop[0][prop_arg_name])
            input_attr = ""

            safe_argument_config = {} if argument_config is None else argument_config

            for decorator_arg_name, decorator_arg_dict in safe_argument_config.items():
                if isinstance(decorator_arg_name, str):
                    decorator_arg_names = [decorator_arg_name]
                else:
                    decorator_arg_names = list(decorator_arg_name)
                for decorator_arg_name in decorator_arg_names:
                    if decorator_arg_name not in decorated_params:
                        decorated_params[decorator_arg_name] = {}

                    treat_as_config = decorator_arg_dict.get("treat_as", "config")
                    decorated_params[decorator_arg_name]["treat_as"] = treat_as_config
                    if treat_as_config != "config":
                        input_attr = decorator_arg_dict["treat_as"] if input_attr == "" else input_attr
                        if input_attr != decorator_arg_dict["treat_as"]:
                            raise Exception(f"{function_name} input type doesn't match")

                    for prop_key in ["widget", "label", "whitelist", "example"]:
                        if prop_key in decorator_arg_dict:
                            if prop_key == "label":
                                decorated_params[decorator_arg_name]["title"] = decorator_arg_dict[prop_key]
                            elif prop_key == "widget":
                                decorated_params[decorator_arg_name][prop_key] = parse_widget(decorator_arg_dict[prop_key])
                            else:
                                decorated_params[decorator_arg_name][prop_key] = decorator_arg_dict[prop_key]

                    if "whitelist" in decorated_params[decorator_arg_name] and "example" in decorated_params[decorator_arg_name]:
                        raise Exception(f"{function_name}: {decorator_arg_name} has both an example and a whitelist")

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                decorated_params[function_arg_name] = decorated_params.get(function_arg_name, {})
                decorated_params[function_arg_name]["treat_as"] = decorated_params[function_arg_name].get("treat_as", "config")

                function_arg_type_dict = get_type_dict(function_param.annotation)
                decorated_params[function_arg_name].update(function_arg_type_dict)
                default_example = function_param.default
                if not default_example is inspect._empty:
                    decorated_params[function_arg_name]["default"] = default_example
                elif decorated_params[function_arg_name]["type"] == "bool":
                    decorated_params[function_arg_name]["default"] = False
                elif "optional" in decorated_params[function_arg_name] and \
                        decorated_params[function_arg_name]["optional"]:
                    decorated_params[function_arg_name]["default"] = None
                if function_arg_name not in json_schema_props:
                    json_schema_props[function_arg_name] = {}
                if "widget" in decorated_params[function_arg_name]:
                    widget = decorated_params[function_arg_name]["widget"]
                else:
                    if function_arg_type_dict is None:
                        widget = "json"
                    else:
                        if function_arg_type_dict["type"] in ["list", "dict", "typing.Dict"]:
                            widget = "json"
                        else:
                            widget = ""

                widget = function_param_to_widget(function_param.annotation, widget)
                param_type = "object" if function_arg_type_dict is None else function_arg_type_dict["type"]
                if hasattr(function_param.annotation, "__funix__"):
                    if hasattr(function_param.annotation, "__funix_bool__"):
                        new_function_arg_type_dict = get_type_dict(bool)
                    else:
                        if hasattr(function_param.annotation, "__funix_base__"):
                            new_function_arg_type_dict = get_type_dict(function_param.annotation.__funix_base__)
                        else:
                            new_function_arg_type_dict = get_type_dict(function_param.annotation.__base__)
                    if new_function_arg_type_dict is not None:
                        param_type = new_function_arg_type_dict["type"]
                json_schema_props[function_arg_name] = get_type_widget_prop(
                    param_type,
                    0,
                    widget,
                    {} if "widget" in decorated_params[function_arg_name] else parsed_theme[1],
                    function_param.annotation
                )

                for prop_key in ["whitelist", "example", "keys", "default", "title"]:
                    if prop_key in decorated_params[function_arg_name].keys():
                        json_schema_props[function_arg_name][prop_key] = decorated_params[function_arg_name][prop_key]

                if "whitelist" in json_schema_props[function_arg_name] and "example" in json_schema_props[function_arg_name]:
                    raise Exception(f"{function_name}: {function_arg_name} has both an example and a whitelist")

                json_schema_props[function_arg_name]["customLayout"] = decorated_params[function_arg_name].get("customLayout", False)

                if decorated_params[function_arg_name]["treat_as"] == "cell":
                    return_type_parsed = "array"
                    json_schema_props[function_arg_name]["items"] = \
                        get_type_widget_prop(
                            param_type,
                            0,
                            widget[1:],
                            {} if "widget" in decorated_params[function_arg_name] else parsed_theme[1],
                            function_param.annotation
                        )
                    json_schema_props[function_arg_name]["type"] = "array"

            all_of = []
            delete_keys = set()
            safe_conditional_visible = {} if conditional_visible is None else conditional_visible

            for conditional_visible_item in safe_conditional_visible:
                config = {
                    "if": {
                        "properties": {}
                    },
                    "then": {
                        "properties": {}
                    },
                    "required": []
                }
                if_items: Any = conditional_visible_item["if"]
                then_items = conditional_visible_item["then"]
                for if_item in if_items.keys():
                    config["if"]["properties"][if_item] = {
                        "const": if_items[if_item]
                    }
                for then_item in then_items:
                    config["then"]["properties"][then_item] = json_schema_props[then_item]
                    config["required"].append(then_item)
                    delete_keys.add(then_item)
                all_of.append(config)

            for key in delete_keys:
                json_schema_props.pop(key)

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
                    "title": function_title,
                    "description": description,
                    "type": "object",
                    "properties": keep_ordered_dict,
                    "allOf": all_of,
                    "input_layout": return_input_layout,
                    "output_layout": return_output_layout,
                    "output_indexes": return_output_indexes
                },
                "destination": destination,
                "source": source_code,
            }

            get_wrapper = app.get(f"/param/{endpoint}")

            def decorated_function_param_getter():
                return flask.Response(json.dumps(decorated_function), mimetype="application/json")

            decorated_function_param_getter.__setattr__("__name__", f"{function_name}_param_getter")
            get_wrapper(decorated_function_param_getter)

            if secret:
                @app.post(f"/verify/{endpoint}")
                @app.post(f"/verify/{id}")
                def verify_secret():
                    data = flask.request.get_json()
                    if data is None:
                        return flask.Response(json.dumps({
                            "success": False,
                        }), mimetype="application/json", status=400)

                    if "secret" not in data:
                        return flask.Response(json.dumps({
                            "success": False,
                        }), mimetype="application/json", status=400)

                    user_secret = flask.request.get_json()["secret"]
                    if user_secret == __decorated_secret_functions_dict[id]:
                        return flask.Response(json.dumps({
                            "success": True,
                        }), mimetype="application/json", status=200)
                    else:
                        return flask.Response(json.dumps({
                            "success": False,
                        }), mimetype="application/json", status=400)

            @wraps(function)
            def wrapper():
                try:
                    function_kwargs = flask.request.get_json()

                    def change_fig_width(figure):
                        fig = mpld3.fig_to_dict(figure)
                        fig["width"] = 560
                        return fig

                    @wraps(function)
                    def wrapped_function(**wrapped_function_kwargs):
                        try:
                            if return_type_parsed == "Figure":
                                fig = function(**wrapped_function_kwargs)
                                return [change_fig_width(fig)]
                            if return_type_parsed in __supported_basic_file_types:
                                return [get_static_uri(function(**wrapped_function_kwargs))]
                            else:
                                result = function(**wrapped_function_kwargs)
                                if isinstance(result, list):
                                    return [result]
                                if not isinstance(result, (str, dict, tuple)):
                                    result = json.dumps(result)
                                if cast_to_list_flag:
                                    result = list(result)
                                else:
                                    if isinstance(result, (str, dict)):
                                        result = [result]
                                    if isinstance(result, tuple):
                                        result = list(result)
                                if result and isinstance(result, list):
                                    if isinstance(return_type_parsed, list):
                                        for index, single_return_type in enumerate(return_type_parsed):
                                            if single_return_type == "Figure":
                                                result[index] = change_fig_width(result[index])
                                            if single_return_type in __supported_basic_file_types:
                                                if type(result[index]) == "list":
                                                    result[index] = [get_static_uri(each) for each in result[index]] # type: ignore
                                                else:
                                                    result[index] = get_static_uri(result[index]) # type: ignore
                                        return result
                                    else:
                                        if return_type_parsed == "Figure":
                                            result = [change_fig_width(result[0])]
                                        if return_type_parsed in __supported_basic_file_types:
                                            if type(result[0]) == "list":
                                                result = [[get_static_uri(each) for each in result[0]]]
                                            else:
                                                result = [get_static_uri(result[0])]
                                        return result
                                return result
                        except:
                            return {
                                "error_type": "function",
                                "error_body": traceback.format_exc()
                            }

                    cell_names = []
                    upload_base64_files = {}
                    for key in json_schema_props.keys():
                        if "treat_as" in json_schema_props[key]:
                            if json_schema_props[key]["treat_as"] == "cell":
                                cell_names.append(key)
                        if "widget" in json_schema_props[key]:
                            if json_schema_props[key]["widget"] in __supported_upload_widgets:
                                upload_base64_files[key] = "single"
                        if "items" in json_schema_props[key]:
                            if "widget" in json_schema_props[key]["items"]:
                                if json_schema_props[key]["items"]["widget"] in __supported_upload_widgets:
                                    upload_base64_files[key] = "multiple"

                    if function_kwargs is None:
                        return {"error_type": "wrapper", "error_body": "No arguments passed to function."}
                    if secret:
                        if "__funix_secret" in function_kwargs:
                            if not __decorated_secret_functions_dict[id] == function_kwargs["__funix_secret"]:
                                return {
                                    "error_type": "wrapper",
                                    "error_body": "Provided secret is incorrect."
                                }
                            else:
                                del function_kwargs["__funix_secret"]
                        else:
                            return {
                                "error_type": "wrapper",
                                "error_body": "No secret provided."
                            }

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
                            temp_result = wrapped_function(**arg)
                            if isinstance(temp_result, list):
                                result.extend(temp_result)
                            else:
                                result.append(temp_result)
                        return [{"result": result}]
                    elif len(upload_base64_files) > 0:
                        new_args = function_kwargs
                        for key in upload_base64_files.keys():
                            if upload_base64_files[key] == "single":
                                with urlopen(function_kwargs[key]) as rsp:
                                    new_args[key] = rsp.read()
                            elif upload_base64_files[key] == "multiple":
                                for index, each in enumerate(function_kwargs[key]):
                                    with urlopen(each) as rsp:
                                        new_args[key][index] = rsp.read()
                        return wrapped_function(**new_args)
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


def funix_parser_backend(config: Optional[str] = None, parser: Literal["json5", "yaml"] = "json5"):
    def decorator(function: Callable):
        if config is None:
            return funix()(function)
        else:
            if parser == "json5":
                jsonConfig: Any = json5.loads(config)
            elif parser == "yaml":
                jsonConfig = yaml.load(config, Loader=yaml.FullLoader)
            else:
                raise ValueError(f"Unknown parser: {parser}")
            return funix(**jsonConfig)(function)
    return decorator


def funix_json5(config: Optional[str] = None):
    return funix_parser_backend(config, "json5")


def funix_yaml(config: Optional[str] = None):
    return funix_parser_backend(config, "yaml")


def new_funix_type(widget: str, config_func: Optional[Callable] = None):
    def decorator(cls):
        if config_func is None:
            cls.__funix__ = True
            cls.__funix_widget__ = widget
            cls.__funix_base__ = cls.__base__
            return cls
        else:
            def new_cls_func(*args, **kwargs):
                cls.__funix__ = True
                cls.__funix_widget__ = widget
                cls.__funix_base__ = cls.__base__
                cls.__funix_config__ = config_func(*args, **kwargs)[1]
                return cls
            return new_cls_func
    return decorator


def export_secrets():
    __new_dict = {}
    for function_id, secret in __decorated_secret_functions_dict.items():
        __new_dict[__decorated_id_to_function_dict[function_id]] = secret
    return __new_dict
