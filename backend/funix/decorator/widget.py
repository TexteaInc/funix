import base64
import json
import pathlib
import re
from inspect import Parameter, signature
from types import MappingProxyType
from typing import Any, Callable, Union

from funix.app import app
from funix.decorator.lists import (
    get_class_method_funix,
    get_function_detail_by_uuid,
    get_function_uuid_with_id,
)
from funix.hint import HTML, ArgumentConfigType
from funix.widget import generate_frontend_widget_config


def create_decorated_params(arg_name: str, decorated_params: dict) -> None:
    """
    Creates a decorated_params entry for the given arg_name if it doesn't exist

    Parameters:
        arg_name (str): The name of the argument
        decorated_params (dict): The decorated_params
    """
    if arg_name not in decorated_params:
        decorated_params[arg_name] = {}


def put_props_in_params(
    arg_name: str, prop_name: str, prop_value: Any, decorated_params: dict
) -> None:
    """
    Puts the given prop_name and prop_value in the decorated_params entry for the given arg_name

    Parameters:
        arg_name (str): The name of the argument
        prop_name (str): The name of the prop
        prop_value (Any): The value of the prop
        decorated_params (dict): The decorated_params
    """
    create_decorated_params(arg_name, decorated_params)
    decorated_params[arg_name][prop_name] = prop_value


def check_example_whitelist(
    arg_name: str, decorated_params: dict, function_name: str
) -> None:
    """
    Checks if the given arg_name has both an example and a whitelist

    Parameters:
        arg_name (str): The name of the argument
        decorated_params (dict): The decorated_params
        function_name (str): The name of the function

    Raises:
        ValueError: If the given arg_name has both an example and a whitelist
    """
    if arg_name in decorated_params:
        if (
            "example" in decorated_params[arg_name]
            and "whitelist" in decorated_params[arg_name]
        ):
            raise ValueError(
                f"{function_name}: {arg_name} has both an example and a whitelist"
            )


def parse_widget(
    widget_info: str | tuple | list | dict,
) -> list[str] | str | dict:
    """
    Parses the given widget_info

    Parameters:
        widget_info (str | tuple | list | dict): The widget_info to parse

    Returns:
        list[str] | str | dict: The widget
    """
    if isinstance(widget_info, dict):
        widget_name = widget_info["widget"]
        widget_config: Union[dict, None] = widget_info.get("props", None)
        if widget_name.startswith("@"):
            return widget_info
        else:
            if widget_config is None:
                return widget_name
            else:
                return generate_frontend_widget_config((widget_name, widget_config))
    if isinstance(widget_info, str):
        return widget_info
    elif isinstance(widget_info, tuple):
        return generate_frontend_widget_config(widget_info)
    elif isinstance(widget_info, list):
        widget_result = []
        for widget_item in widget_info:
            if isinstance(widget_item, tuple):
                widget_result.append(generate_frontend_widget_config(widget_item))
            elif isinstance(widget_item, list):
                widget_result.append(parse_widget(widget_item))
            elif isinstance(widget_item, str):
                widget_result.append(widget_item)
        return widget_result


def iter_over_prop(
    argument_type: str,
    argument: dict[str | tuple, Any] | None,
    function_params_name: list[str],
    decorated_params: dict,
    function_name: str,
    callback,
):
    """
    callback: pass in (argument_type, key, key_idx, value)
    """
    if argument is None:
        return

    for arg_idx, arg_key in enumerate(argument):
        if isinstance(arg_key, str):
            callback(
                argument_type,
                arg_key,
                0,
                argument[arg_key],
                function_params_name,
                decorated_params,
                function_name,
            )
        elif isinstance(arg_key, tuple):
            for key_idx, single_key in enumerate(arg_key):
                callback(
                    argument_type,
                    single_key,
                    key_idx,
                    argument[arg_key],
                    function_params_name,
                    decorated_params,
                    function_name,
                )
        else:
            raise TypeError(
                f"Argument `{argument_type}` has invalid key type {type(argument)}"
            )


def expand_wildcards(origin_key: str, search_list: list[str]) -> list[str]:
    keys = []
    if "*" in origin_key or "?" in origin_key:
        for param_name in search_list:
            if pathlib.PurePath(param_name).match(origin_key):
                keys.append(param_name)
    elif origin_key.startswith("regex:"):
        regex = re.compile(origin_key[6:])
        for param_name in search_list:
            if regex.search(param_name) is not None:
                keys.append(param_name)
    else:
        keys.append(origin_key)
    return keys


def process_widgets(
    arg_type: str,
    arg_key: str,
    _key_idx: int,
    value: any,
    function_params_name: list,
    decorated_params: dict,
    _function_name: str,
):
    parsed_widget = parse_widget(value)
    for expanded_key in expand_wildcards(arg_key, function_params_name):
        put_props_in_params(expanded_key, arg_type, parsed_widget, decorated_params)


def process_title(
    arg_type: str,
    arg_key: str,
    _key_idx: int,
    value: any,
    function_params_name: list,
    decorated_params: dict,
    _function_name: str,
):
    for expanded_key in expand_wildcards(arg_key, function_params_name):
        put_props_in_params(expanded_key, arg_type, value, decorated_params)


def process_treat_as(
    arg_type: str,
    arg_key: str,
    _key_idx: int,
    value: any,
    _function_params_name: list,
    decorated_params: dict,
    _function_name: str,
):
    put_props_in_params(arg_key, arg_type, value, decorated_params)


def process_examples_and_whitelist(
    arg_type: str,
    arg_key: str,
    _key_idx: int,
    value: any,
    _function_params_name: list,
    decorated_params: dict,
    function_name: str,
):
    if isinstance(value, list):
        # is a 2d or more dimension list
        if isinstance(value[_key_idx], list):
            put_props_in_params(arg_key, arg_type, value[_key_idx], decorated_params)
        else:
            put_props_in_params(arg_key, arg_type, value, decorated_params)
    else:
        put_props_in_params(arg_key, arg_type, value, decorated_params)
    check_example_whitelist(arg_key, decorated_params, function_name)


def widget_parse(
    function_params: MappingProxyType[str, Parameter],
    decorated_params: dict,
    function_name: str,
    widgets: dict,
    argument_labels: dict,
    treat_as: dict,
    examples: dict,
    whitelist: dict,
    param_widget_whitelist_callable: dict,
    param_widget_example_callable: dict,
):
    function_params_name: list[str] = list(function_params.keys())

    for i in [
        ("widget", widgets, process_widgets),
        ("title", argument_labels, process_title),
        ("treat_as", treat_as, process_treat_as),
        ("example", examples, process_examples_and_whitelist),
        ("whitelist", whitelist, process_examples_and_whitelist),
    ]:
        iter_over_prop(
            i[0],
            i[1],
            function_params_name,
            decorated_params,
            function_name,
            i[2],
        )
    if examples:
        for example, example_value in examples.items():
            if callable(example_value):
                param_widget_example_callable[example] = example_value

    if whitelist:
        for whitelist_, whitelist_value in whitelist.items():
            if callable(whitelist_value):
                param_widget_whitelist_callable[whitelist_] = whitelist_value


def parse_argument_config(
    argument_config: ArgumentConfigType,
    decorated_params: dict,
    function_name: str,
):
    input_attr = ""
    for decorator_arg_name, decorator_arg_dict in argument_config.items():
        if isinstance(decorator_arg_name, str):
            decorator_arg_names = [decorator_arg_name]
        else:
            decorator_arg_names = list(decorator_arg_name)
        for single_decorator_arg_name in decorator_arg_names:
            if single_decorator_arg_name not in decorated_params:
                decorated_params[single_decorator_arg_name] = {}

            treat_as_config = decorator_arg_dict.get("treat_as", "config")
            decorated_params[single_decorator_arg_name]["treat_as"] = treat_as_config
            if treat_as_config != "config":
                input_attr = (
                    decorator_arg_dict["treat_as"] if input_attr == "" else input_attr
                )
                if input_attr != decorator_arg_dict["treat_as"]:
                    raise Exception(f"{function_name} input type doesn't match")

            for prop_key in ["widget", "label", "whitelist", "example"]:
                if prop_key in decorator_arg_dict:
                    if prop_key == "label":
                        decorated_params[single_decorator_arg_name][
                            "title"
                        ] = decorator_arg_dict[prop_key]
                    elif prop_key == "widget":
                        decorated_params[single_decorator_arg_name][
                            prop_key
                        ] = parse_widget(decorator_arg_dict[prop_key])
                    else:
                        decorated_params[single_decorator_arg_name][
                            prop_key
                        ] = decorator_arg_dict[prop_key]

            if (
                "whitelist" in decorated_params[single_decorator_arg_name]
                and "example" in decorated_params[single_decorator_arg_name]
            ):
                raise Exception(
                    f"{function_name}: {single_decorator_arg_name} has both an example and a whitelist"
                )


def generate_redirect_link(
    function: Callable,
    *args,
    **kwargs,
) -> HTML:
    """
    Generate a redirect link.

    Parameters:
        function(Callable): The function.
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        str | Markdown | HTML: The result.
    """
    function_qualname = function.__qualname__
    _function = function
    if "." in function_qualname:
        class_function = get_class_method_funix(
            app_name=app.name, method_qualname=function_qualname
        )
        if class_function:
            _function = class_function
        else:
            raise ValueError(f"Function {function_qualname} not found.")
    jump_uuid = get_function_uuid_with_id(app_name=app.name, _id=id(_function))
    if jump_uuid == "":
        raise ValueError(f"Function {function_qualname} not found.")
    result = get_function_detail_by_uuid(app_name=app.name, uuid=jump_uuid)
    arguments = signature(_function).bind(*args, **kwargs)
    arguments.apply_defaults()
    dict_args = arguments.arguments
    json_plain = json.dumps(dict_args)
    web_safe_args = base64.urlsafe_b64encode(json_plain.encode()).decode()
    return f"<a href='/{result['path']}?args={web_safe_args}'>{result['name']}</a>"
