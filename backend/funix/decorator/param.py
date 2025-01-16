from copy import deepcopy
from inspect import Parameter
from json import dumps
from types import MappingProxyType
from typing import Any, Callable

from flask import Response

from funix.config.switch import GlobalSwitchOption
from funix.decorator.annnotation_analyzer import analyze
from funix.decorator.lists import get_class
from funix.decorator.magic import (
    function_param_to_widget,
    get_type_dict,
    get_type_widget_prop,
)
from funix.session import get_global_variable

dataframe_parse_metadata: dict[str, dict[str, list[str]]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""

parse_type_metadata: dict[str, dict[str, Any]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""


def parse_param(
    function_params: MappingProxyType[str, Parameter],
    json_schema_props: dict,
    decorated_params: dict,
    pandas_use: bool,
    pandas_module: Any,
    pandera_module: Any,
    function_id: str,
    function_name: str,
    parsed_theme: Any,
) -> str | None:
    global dataframe_parse_metadata, parse_type_metadata
    return_type_parsed = None
    for _, function_param in function_params.items():
        if pandas_use:
            anno = function_param.annotation
            default_values = (
                {}
                if function_param.default is Parameter.empty
                else function_param.default
            )

            def analyze_columns_and_default_value(pandas_like_anno):
                column_names = []
                dataframe_parse_metadata[function_id] = dataframe_parse_metadata.get(
                    function_id, {}
                )
                columns = {}
                if isinstance(pandas_like_anno.columns, dict):
                    columns = pandas_like_anno.columns
                else:
                    # Should be Index here
                    for column_name in pandas_like_anno.columns.to_list():
                        columns[column_name] = {"don't": "check"}
                for name, column in columns.items():
                    if name in default_values:
                        column_default = list(default_values[name])
                    else:
                        column_default = None
                    if hasattr(column, "dtype"):
                        d_type = column.dtype
                        items = analyze(type(d_type))
                        items["widget"] = "sheet"
                    else:
                        if column_default is None:
                            items = {"type": "string", "widget": "sheet"}
                        else:
                            items = get_type_widget_prop(
                                get_type_dict(type(column_default[0]))["type"],
                                0,
                                [],
                                {},
                                None,
                            )
                            items = {
                                "type": items["type"],
                                "widget": "sheet",
                            }
                    column_names.append(name)
                    anal = {
                        "type": "array",
                        "widget": "sheet",
                        "items": items,
                        "customLayout": False,
                        "treat_as": "config",
                    }
                    dec_param = {
                        "widget": "sheet",
                        "treat_as": "config",
                        "type": f"<mock>list[{items['type']}]</mock>",
                    }
                    if column_default:
                        anal["default"] = column_default
                        dec_param["default"] = column_default
                    json_schema_props[name] = anal
                    decorated_params[name] = dec_param
                dataframe_parse_metadata[function_id][
                    function_param.name
                ] = column_names

            if isinstance(anno, pandas_module.DataFrame):
                if anno.columns.size == 0:
                    raise Exception(
                        f"{function_name}: pandas.DataFrame() is not supported, "
                        f"but you can add columns to it, if you mean DataFrame with no columns, "
                        f"please use `pandas.DataFrame` instead."
                    )
                else:
                    analyze_columns_and_default_value(anno)
                    continue

            if anno is pandas_module.core.frame.DataFrame:
                if function_param.default is not Parameter.empty:
                    analyze_columns_and_default_value(default_values)
                else:
                    # Be sheet later
                    json_schema_props[function_param.name] = {
                        "type": "object",
                        "widget": "json",
                        "treat_as": "config",
                        "customLayout": False,
                    }
                    decorated_params[function_param.name] = {
                        "widget": "json",
                        "treat_as": "config",
                    }
                continue
            if (
                hasattr(anno, "__origin__")
                and getattr(anno, "__origin__")
                is pandera_module.typing.pandas.DataFrame
            ):
                if hasattr(anno, "__args__"):
                    model_class = getattr(anno, "__args__")[0]
                    analyze_columns_and_default_value(model_class.to_schema())
                else:
                    raise Exception(
                        "Please give a schema with pandera.DataFrameModel for DataFrame"
                    )
                continue
        parse_type_metadata[function_id][
            function_param.name
        ] = function_param.annotation
        function_arg_name = function_param.name
        decorated_params[function_arg_name] = decorated_params.get(
            function_arg_name, {}
        )
        decorated_params[function_arg_name]["treat_as"] = decorated_params[
            function_arg_name
        ].get("treat_as", "config")

        if GlobalSwitchOption.AUTO_CONVERT_UNDERSCORE_TO_SPACE_IN_NAME:
            if "_" in function_arg_name:
                decorated_params[function_arg_name]["title"] = decorated_params[
                    function_arg_name
                ].get("title", function_arg_name.replace("_", " "))

        function_arg_type_dict = get_type_dict(function_param.annotation)
        decorated_params[function_arg_name].update(function_arg_type_dict)
        default_example = function_param.default
        if default_example is not Parameter.empty:
            decorated_params[function_arg_name]["default"] = default_example
        elif decorated_params[function_arg_name]["type"] == "bool":
            decorated_params[function_arg_name]["default"] = False
        elif (
            "optional" in decorated_params[function_arg_name]
            and decorated_params[function_arg_name]["optional"]
        ):
            decorated_params[function_arg_name]["default"] = None
        if function_arg_name not in json_schema_props:
            json_schema_props[function_arg_name] = {}
        theme_widgets = deepcopy(parsed_theme[1])
        custom_component = None
        custom_component_props = None
        if hasattr(function_param.annotation, "__name__"):
            name = function_param.annotation.__name__
            if name in theme_widgets:
                result = theme_widgets[name]
                if isinstance(result, dict):
                    custom_component = result["widget"]
                    custom_component_props = result.get("props", None)
                    theme_widgets.pop(name)
                elif isinstance(result, str):
                    if result.startswith("@"):
                        custom_component = result
                        theme_widgets.pop(name)
        if "widget" in decorated_params[function_arg_name]:
            widget = decorated_params[function_arg_name]["widget"]
            if isinstance(widget, str):
                if widget.startswith("@"):
                    # Custom component
                    custom_component = widget
                    widget = ""
            elif isinstance(widget, dict):
                custom_component = widget["widget"]
                custom_component_props = widget.get("props", None)
                widget = ""
        else:
            if function_arg_type_dict is None:
                widget = "json"
            else:
                if function_arg_type_dict["type"] in [
                    "dict",
                    "typing.Dict",
                ]:
                    widget = "json"
                else:
                    widget = ""

        if custom_component is not None:
            widget = ""
        widget = function_param_to_widget(function_param.annotation, widget)
        param_type = (
            "object"
            if function_arg_type_dict is None
            else function_arg_type_dict["type"]
        )
        if hasattr(function_param.annotation, "__funix__"):
            if hasattr(function_param.annotation, "__funix_bool__"):
                new_function_arg_type_dict = get_type_dict(bool)
            else:
                if hasattr(function_param.annotation, "__funix_base__"):
                    new_function_arg_type_dict = get_type_dict(
                        function_param.annotation.__funix_base__
                    )
                else:
                    new_function_arg_type_dict = get_type_dict(
                        function_param.annotation.__base__
                    )
            if new_function_arg_type_dict is not None:
                param_type = new_function_arg_type_dict["type"]
        json_schema_props[function_arg_name] = get_type_widget_prop(
            param_type,
            0,
            widget,
            {} if "widget" in decorated_params[function_arg_name] else theme_widgets,
            function_param.annotation,
        )

        for prop_key in ["whitelist", "example", "keys", "default", "title"]:
            if prop_key in decorated_params[function_arg_name].keys():
                json_schema_props[function_arg_name][prop_key] = decorated_params[
                    function_arg_name
                ][prop_key]

        if (
            "whitelist" in json_schema_props[function_arg_name]
            and "example" in json_schema_props[function_arg_name]
        ):
            raise Exception(
                f"{function_name}: {function_arg_name} has both an example and a whitelist"
            )

        json_schema_props[function_arg_name]["customLayout"] = decorated_params[
            function_arg_name
        ].get("customLayout", False)

        if decorated_params[function_arg_name]["treat_as"]:
            json_schema_props[function_arg_name]["treat_as"] = decorated_params[
                function_arg_name
            ]["treat_as"]

        if decorated_params[function_arg_name]["treat_as"] == "cell":
            return_type_parsed = "array"
            json_schema_props[function_arg_name]["items"] = get_type_widget_prop(
                param_type,
                0,
                widget[1:],
                {}
                if "widget" in decorated_params[function_arg_name]
                else theme_widgets,
                function_param.annotation,
            )
            json_schema_props[function_arg_name]["type"] = "array"

        if custom_component is not None:
            json_schema_props[function_arg_name]["funixComponent"] = custom_component
            if custom_component_props is not None:
                json_schema_props[function_arg_name][
                    "funixProps"
                ] = custom_component_props
            json_schema_props[function_arg_name]["type"] = "object"

        if hasattr(function_param.annotation, "__funix_component__"):
            json_schema_props[function_arg_name][
                "funixComponent"
            ] = function_param.annotation.__funix_component__
            if hasattr(function_param.annotation, "__funix_props__"):
                json_schema_props[function_arg_name][
                    "funixProps"
                ] = function_param.annotation.__funix_props__
            json_schema_props[function_arg_name]["type"] = "object"
    return return_type_parsed


def create_parse_type_metadata(function_id: str):
    global parse_type_metadata
    parse_type_metadata[function_id] = {}


def get_real_callable(app: str, function: Callable, qualname: str) -> Callable:
    if function.__name__ == "<lambda>":
        class_ = get_class(app, ".".join(qualname.split(".")[:-1]))
        org = function(get_global_variable("__FUNIX_" + class_.__name__))
        if callable(org):
            return org
        else:
            return lambda: org
    if callable(function):
        return function
    return lambda: function


def get_param_for_funix(
    app_name: str,
    pre_fill: dict | None,
    dynamic_defaults: dict | None,
    decorated_function: dict,
    session_description: str,
    param_widget_whitelist_callable: dict,
    param_widget_example_callable: dict,
    qualname: str,
):
    new_decorated_function = deepcopy(decorated_function)
    if pre_fill is not None:
        for argument_key, from_function_info in pre_fill.items():
            if isinstance(from_function_info, tuple):
                last_result = get_global_variable(
                    app_name
                    + str(id(from_function_info[0]))
                    + f"_{from_function_info[1]}"
                )
            else:
                last_result = get_global_variable(
                    app_name + str(id(from_function_info)) + "_result"
                )
            if last_result is not None:
                new_decorated_function["params"][argument_key]["default"] = last_result
                new_decorated_function["schema"]["properties"][argument_key][
                    "default"
                ] = last_result
    if dynamic_defaults is not None:
        for argument_key, dynamic_default_callable in dynamic_defaults.items():
            if isinstance(argument_key, tuple):
                if isinstance(dynamic_default_callable, tuple):
                    if len(dynamic_default_callable) != len(argument_key):
                        raise ValueError(
                            f"Length of {argument_key} and {dynamic_default_callable} should be the same"
                        )
                    for i, argument_key_ in enumerate(argument_key):
                        real_callable = get_real_callable(
                            app_name, dynamic_default_callable[i], qualname
                        )
                        result = real_callable()
                        new_decorated_function["params"][argument_key_][
                            "default"
                        ] = result
                        new_decorated_function["schema"]["properties"][argument_key_][
                            "default"
                        ] = result
                else:
                    result = get_real_callable(
                        app_name, dynamic_default_callable, qualname
                    )()
                    for argument_key_ in argument_key:
                        new_decorated_function["params"][argument_key_][
                            "default"
                        ] = result
                        new_decorated_function["schema"]["properties"][argument_key_][
                            "default"
                        ] = result
            else:
                real_callable = get_real_callable(
                    app_name, dynamic_default_callable, qualname
                )
                result = real_callable()
                new_decorated_function["params"][argument_key]["default"] = result
                new_decorated_function["schema"]["properties"][argument_key][
                    "default"
                ] = result
    if param_widget_whitelist_callable:
        for (
            whitelist_,
            whitelist_value_callable,
        ) in param_widget_whitelist_callable.items():
            real_callable = get_real_callable(
                app_name, whitelist_value_callable, qualname
            )
            whitelist_value = real_callable()
            new_decorated_function["params"][whitelist_]["whitelist"] = whitelist_value
            new_decorated_function["schema"]["properties"][whitelist_][
                "whitelist"
            ] = whitelist_value

    if param_widget_example_callable:
        for example_, example_value_callable in param_widget_example_callable.items():
            example_value = get_real_callable(
                app_name, example_value_callable, qualname
            )()
            new_decorated_function["params"][example_]["example"] = example_value
            new_decorated_function["schema"]["properties"][example_][
                "example"
            ] = example_value
    if session_description:
        des = get_global_variable(session_description)
        new_decorated_function["description"] = des
        new_decorated_function["schema"]["description"] = des
    return Response(dumps(new_decorated_function), mimetype="application/json")


def get_dataframe_parse_metadata():
    global dataframe_parse_metadata
    return dataframe_parse_metadata


def get_parse_type_metadata():
    global parse_type_metadata
    return parse_type_metadata
