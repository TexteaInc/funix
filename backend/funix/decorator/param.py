import types
from copy import deepcopy
from inspect import Parameter
from json import dumps, JSONEncoder
from types import MappingProxyType
from typing import Any, Callable
from datetime import datetime

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
from funix.decorator.layout import (
    pydantic_layout_dict,
    pydantic_name_dict,
    pydantic_widget_dict,
)

dataframe_parse_metadata: dict[str, dict[str, list[str]]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""

parse_type_metadata: dict[str, dict[str, Any]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""


class FunixJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__class__"):
            clz = o.__class__
            if hasattr(clz, "__base__"):
                base = clz.__base__
                # Check pydantic
                try:
                    from pydantic import BaseModel

                    if issubclass(base, BaseModel):
                        return o.model_dump(mode="json")
                except ImportError:
                    return super().default(o)
        return super().default(o)


def apply_decorated_params(
    item_props: dict, decorated_params: dict, param_name: str, function_name: str = None
) -> None:
    for prop_key in ["whitelist", "example", "keys", "default", "title"]:
        if prop_key in decorated_params:
            item_props[prop_key] = decorated_params[prop_key]

    if "whitelist" in item_props and "example" in item_props:
        error_msg = f"Field {param_name} has both an example and a whitelist"
        if function_name:
            error_msg = f"{function_name}: {error_msg}"
        raise Exception(error_msg)


def create_basic_widget_item(
    annotation: Any, widget: str = "", theme_widgets: dict = None
) -> dict:
    if theme_widgets is None:
        theme_widgets = {}

    type_dict = get_type_dict(annotation)
    return get_type_widget_prop(type_dict["type"], 0, widget, theme_widgets, annotation)


def resolve_param_type(function_param: Parameter, function_arg_type_dict: dict) -> str:
    param_type = (
        "object" if function_arg_type_dict is None else function_arg_type_dict["type"]
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

    return param_type


def create_param_widget_props(
    function_param: Parameter,
    function_arg_type_dict: dict,
    widget: str,
    theme_widgets: dict,
    decorated_params: dict,
    function_arg_name: str,
) -> dict:
    param_type = resolve_param_type(function_param, function_arg_type_dict)

    return get_type_widget_prop(
        param_type,
        0,
        widget,
        {} if "widget" in decorated_params else theme_widgets,
        function_param.annotation,
    )


def apply_custom_component_logic(
    schema_props: dict,
    custom_component: str | None,
    custom_component_props: dict | None,
    annotation: Any,
) -> None:
    if custom_component is not None:
        schema_props["funixComponent"] = custom_component
        if custom_component_props is not None:
            schema_props["funixProps"] = custom_component_props
        schema_props["type"] = "object"

    if hasattr(annotation, "__funix_component__"):
        schema_props["funixComponent"] = annotation.__funix_component__
        if hasattr(annotation, "__funix_props__"):
            schema_props["funixProps"] = annotation.__funix_props__
        schema_props["type"] = "object"


def process_pydantic_field_customization(
    field_name: str,
    field_annotation: Any,
    base_item: dict,
    function_param: Parameter,
    decorated_params: dict,
    parsed_theme: Any,
    funix_arg_name: str,
) -> dict:
    arg_type_dict = get_type_dict(field_annotation)

    if funix_arg_name not in decorated_params:
        theme_widgets, widget, custom_component, custom_component_props = (
            param_to_widget(
                parsed_theme,
                function_param,
                {funix_arg_name: {}},
                funix_arg_name,
                arg_type_dict,
            )
        )
    else:
        theme_widgets, widget, custom_component, custom_component_props = (
            param_to_widget(
                parsed_theme,
                function_param,
                decorated_params,
                funix_arg_name,
                arg_type_dict,
            )
        )

    if funix_arg_name not in decorated_params:
        widget_props = create_param_widget_props(
            function_param,
            arg_type_dict,
            widget,
            theme_widgets,
            {},
            funix_arg_name,
        )
    else:
        widget_props = create_param_widget_props(
            function_param,
            arg_type_dict,
            widget,
            theme_widgets,
            decorated_params[funix_arg_name],
            funix_arg_name,
        )
    merged_item = {**base_item, **widget_props}

    apply_custom_component_logic(
        merged_item, custom_component, custom_component_props, field_annotation
    )

    if funix_arg_name not in decorated_params:
        apply_decorated_params(merged_item, {}, funix_arg_name)
    else:
        apply_decorated_params(
            merged_item, decorated_params[funix_arg_name], funix_arg_name
        )
    return merged_item


def get_basic_pydantic_items(
    anno: Any,
    function_param: Parameter,
    decorated_params: dict,
    parsed_theme: Any,
    sub_field_name: str | None = None,
    widgets: dict | None = None,
) -> dict:
    from pydantic_core import PydanticUndefinedType

    items = {}
    for field_name, field in anno.__pydantic_fields__.items():
        anno_ = field.annotation
        is_array = False
        is_optional = False
        if type(anno_) is types.UnionType:
            is_optional = True
            anno_ = anno_.__args__[0]
        if hasattr(anno_, "__name__"):
            if anno_.__name__ == "Optional":
                is_optional = True
                anno_ = anno_.__args__[0]
            if anno_.__name__ in ["list", "List"]:
                is_array = True
                anno_ = anno_.__args__[0]

        items[field_name] = create_basic_widget_item(anno_)

        if not isinstance(field.default, PydanticUndefinedType):
            items[field_name]["default"] = field.default

        if not field.examples is None:
            items[field_name]["example"] = field.examples

        if not field.title is None:
            items[field_name]["title"] = field.title

        if not field.description is None:
            if "title" not in items[field_name]:
                items[field_name]["title"] = field.description
            else:
                items[field_name]["title"] += f" ({field.description})"

        if not field.is_required():
            items[field_name]["optional"] = True

        if is_optional:
            items[field_name]["optional"] = True

        funix_arg_name = f"{function_param.name}"
        if sub_field_name is not None:
            funix_arg_name += f".{sub_field_name}"
        funix_arg_name += f".{field_name}"

        items[field_name] = process_pydantic_field_customization(
            field_name,
            anno_,
            items[field_name],
            function_param,
            decorated_params,
            parsed_theme,
            funix_arg_name,
        )

        if widgets is not None and field_name in widgets:
            items[field_name]["widget"] = widgets[field_name]

        if hasattr(anno_, "__pydantic_fields__"):
            pydantic_widgets = None
            if id(anno_) in pydantic_widget_dict:
                pydantic_widgets = pydantic_widget_dict[id(anno_)]
            items[field_name]["type"] = "array" if is_array else "object"
            items[field_name]["items"] = {
                "type": "object",
                "properties": get_basic_pydantic_items(
                    anno_,
                    function_param,
                    decorated_params,
                    parsed_theme,
                    field_name,
                    pydantic_widgets,
                ),
                "widget": "__object_complex_pydantic",
            }
            items[field_name]["widget"] = (
                "__array_complex_pydantic" if is_array else "__object_complex_pydantic"
            )
            if id(anno_) in pydantic_layout_dict:
                layout_tuple = pydantic_layout_dict[id(anno_)]
                items[field_name]["pydantic_layout"] = layout_tuple[0]
                items[field_name]["items"]["pydantic_layout"] = layout_tuple[0]
            if id(anno_) in pydantic_name_dict:
                items[field_name]["pydantic_title"] = pydantic_name_dict[id(anno_)]
                items[field_name]["items"]["pydantic_title"] = pydantic_name_dict[
                    id(anno_)
                ]
        else:
            if is_array:
                items[field_name]["items"] = deepcopy(items[field_name])
                items[field_name]["type"] = "array"
    return items


def wrap_pydantic_items(items: dict, function_param: Parameter) -> dict:
    anal = {
        "type": "object",
        "widget": "__object_complex_pydantic",
        "__message": "This is an experimental attempt.",
        "treat_as": "config",
        "items": items,
    }
    dec_param = {
        "widget": "__object_complex_pydantic",
        "treat_as": "config",
        "type": "<mock>please check `pydantic_items` field.</mock>",
        "pydantic_items": items,
    }
    if function_param.default is not Parameter.empty:
        anal["default"] = function_param.default.model_dump(mode="json")
        dec_param["default"] = function_param.default.model_dump(mode="json")
    return anal, dec_param


def param_to_widget(
    parsed_theme: Any,
    function_param: Parameter,
    decorated_params: dict,
    function_arg_name: str,
    function_arg_type_dict: dict,
) -> dict:
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
    return theme_widgets, widget, custom_component, custom_component_props


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

        theme_widgets, widget, custom_component, custom_component_props = (
            param_to_widget(
                parsed_theme,
                function_param,
                decorated_params,
                function_arg_name,
                function_arg_type_dict,
            )
        )

        json_schema_props[function_arg_name] = create_param_widget_props(
            function_param,
            function_arg_type_dict,
            widget,
            theme_widgets,
            decorated_params[function_arg_name],
            function_arg_name,
        )

        apply_decorated_params(
            json_schema_props[function_arg_name],
            decorated_params[function_arg_name],
            function_arg_name,
            function_name,
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
            param_type = resolve_param_type(function_param, function_arg_type_dict)
            json_schema_props[function_arg_name]["items"] = get_type_widget_prop(
                param_type,
                0,
                widget[1:],
                (
                    {}
                    if "widget" in decorated_params[function_arg_name]
                    else theme_widgets
                ),
                function_param.annotation,
            )
            json_schema_props[function_arg_name]["type"] = "array"

        apply_custom_component_logic(
            json_schema_props[function_arg_name],
            custom_component,
            custom_component_props,
            function_param.annotation,
        )
        # Pydantic check, this so complex, so there will be a lot of bugs
        # should be like:
        # `List[SingleModel]` -> `__array_complex_pydantic`
        # `SingleModel` -> `__object_complex_pydantic`
        anno = function_param.annotation
        is_array = False
        is_optional = False
        if type(anno) is types.UnionType:
            is_optional = True
            anno = anno.__args__[0]
        if hasattr(anno, "__name__"):
            if anno.__name__ == "Optional":
                is_optional = True
                anno = anno.__args__[0]
            if anno.__name__ in ["list", "List"]:
                is_array = True
                anno = anno.__args__[0]
        if hasattr(anno, "__pydantic_fields__"):
            pydantic_widget = None
            if id(anno) in pydantic_widget_dict:
                pydantic_widget = pydantic_widget_dict[id(anno)]
            anal, dec_param = wrap_pydantic_items(
                get_basic_pydantic_items(
                    anno,
                    function_param,
                    decorated_params[function_arg_name],
                    parsed_theme,
                    widgets=pydantic_widget,
                ),
                function_param,
            )
            json_schema_props[function_arg_name]["type"] = (
                "array" if is_array else "object"
            )
            json_schema_props[function_arg_name]["items"] = {
                "type": "object",
                "properties": anal["items"],
            }
            json_schema_props[function_arg_name]["treat_as"] = "config"
            json_schema_props[function_arg_name]["widget"] = (
                "__array_complex_pydantic" if is_array else "__object_complex_pydantic"
            )
            json_schema_props[function_arg_name][
                "__message"
            ] = "This is an experimental attempt."
            if id(anno) in pydantic_layout_dict:
                layout_tuple = pydantic_layout_dict[id(anno)]
                json_schema_props[function_arg_name]["pydantic_layout"] = layout_tuple[
                    0
                ]
                json_schema_props[function_arg_name]["items"]["pydantic_layout"] = (
                    layout_tuple[0]
                )
            if id(anno) in pydantic_name_dict:
                json_schema_props[function_arg_name]["pydantic_title"] = (
                    pydantic_name_dict[id(anno)]
                )
                json_schema_props[function_arg_name]["items"]["pydantic_title"] = (
                    pydantic_name_dict[id(anno)]
                )
            decorated_params[function_arg_name]["widget"] = (
                "__array_complex_pydantic" if is_array else "__object_complex_pydantic"
            )
            decorated_params[function_arg_name]["treat_as"] = "config"
            decorated_params[function_arg_name][
                "type"
            ] = "<mock>please check `pydantic_items` field.</mock>"
            decorated_params[function_arg_name]["pydantic_items"] = anal["items"]
            if id(anno) in pydantic_layout_dict:
                layout_tuple = pydantic_layout_dict[id(anno)]
                decorated_params[function_arg_name]["pydantic_layout"] = layout_tuple[
                    0
                ]  # layout_list
            if id(anno) in pydantic_name_dict:
                decorated_params[function_arg_name]["pydantic_title"] = (
                    pydantic_name_dict[id(anno)]
                )

            if is_optional:
                json_schema_props[function_arg_name]["optional"] = True
                decorated_params[function_arg_name]["optional"] = True

    return return_type_parsed


def create_parse_type_metadata(function_id: str):
    global parse_type_metadata
    parse_type_metadata[function_id] = {}


def get_real_callable(app: str, function: Callable, qualname: str) -> Callable:
    if function.__name__ == "<lambda>":
        class_ = get_class(app, ".".join(qualname.split(".")[:-1]))
        if class_ is not None:
            org = function(get_global_variable("__FUNIX_" + class_.__name__))
            if callable(org):
                return org
            else:
                return lambda: org
        else:
            return function
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
                if "." in argument_key:
                    argument_key_list = argument_key.split(".")
                    first_element, *rest = argument_key_list
                    window_params = new_decorated_function["params"][first_element]
                    for rest_element in rest:
                        window_params = window_params["items"]["properties"][
                            rest_element
                        ]
                    window_params["default"] = last_result
                    window_schema = new_decorated_function["schema"]["properties"][
                        first_element
                    ]
                    for rest_element in rest:
                        window_schema = window_schema["items"]["properties"][
                            rest_element
                        ]
                    window_schema["default"] = last_result
                else:
                    new_decorated_function["params"][argument_key][
                        "default"
                    ] = last_result
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
                        if "." in argument_key_:
                            argument_key_list = argument_key_.split(".")
                            first_element, *rest = argument_key_list
                            window_params = new_decorated_function["params"][
                                first_element
                            ]
                            for rest_element in rest:
                                window_params = window_params["items"]["properties"][
                                    rest_element
                                ]
                            window_params["default"] = result
                            window_schema = new_decorated_function["schema"][
                                "properties"
                            ][first_element]
                            for rest_element in rest:
                                window_schema = window_schema["items"]["properties"][
                                    rest_element
                                ]
                            window_schema["default"] = result
                        else:
                            new_decorated_function["params"][argument_key_][
                                "default"
                            ] = result
                            new_decorated_function["schema"]["properties"][
                                argument_key_
                            ]["default"] = result
                else:
                    result = get_real_callable(
                        app_name, dynamic_default_callable, qualname
                    )()
                    for argument_key_ in argument_key:
                        if "." in argument_key_:
                            argument_key_list = argument_key_.split(".")
                            first_element, *rest = argument_key_list
                            window_params = new_decorated_function["params"][
                                first_element
                            ]
                            for rest_element in rest:
                                window_params = window_params["items"]["properties"][
                                    rest_element
                                ]
                            window_params["default"] = result
                            window_schema = new_decorated_function["schema"][
                                "properties"
                            ][first_element]
                            for rest_element in rest:
                                window_schema = window_schema["items"]["properties"][
                                    rest_element
                                ]
                            window_schema["default"] = result
                        else:
                            new_decorated_function["params"][argument_key_][
                                "default"
                            ] = result
                            new_decorated_function["schema"]["properties"][
                                argument_key_
                            ]["default"] = result
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
            if "." in whitelist_:
                whitelist_key_list = whitelist_.split(".")
                first_element, *rest = whitelist_key_list
                window_params = new_decorated_function["params"][first_element]
                for rest_element in rest:
                    window_params = window_params["items"]["properties"][rest_element]
                window_params["whitelist"] = whitelist_value
                window_schema = new_decorated_function["schema"]["properties"][
                    first_element
                ]
                for rest_element in rest:
                    window_schema = window_schema["items"]["properties"][rest_element]
                window_schema["whitelist"] = whitelist_value
            else:
                new_decorated_function["params"][whitelist_][
                    "whitelist"
                ] = whitelist_value
                new_decorated_function["schema"]["properties"][whitelist_][
                    "whitelist"
                ] = whitelist_value

    if param_widget_example_callable:
        for example_, example_value_callable in param_widget_example_callable.items():
            example_value = get_real_callable(
                app_name, example_value_callable, qualname
            )()
            if "." in example_:
                example_key_list = example_.split(".")
                first_element, *rest = example_key_list
                window_params = new_decorated_function["params"][first_element]
                for rest_element in rest:
                    window_params = window_params["items"]["properties"][rest_element]
                window_params["example"] = example_value
                window_schema = new_decorated_function["schema"]["properties"][
                    first_element
                ]
                for rest_element in rest:
                    window_schema = window_schema["items"]["properties"][rest_element]
                window_schema["example"] = example_value
            else:
                new_decorated_function["params"][example_]["example"] = example_value
                new_decorated_function["schema"]["properties"][example_][
                    "example"
                ] = example_value
    if session_description:
        des = get_global_variable(session_description)
        new_decorated_function["description"] = des
        new_decorated_function["schema"]["description"] = des
    return Response(
        dumps(new_decorated_function, cls=FunixJsonEncoder), mimetype="application/json"
    )


def get_dataframe_parse_metadata():
    global dataframe_parse_metadata
    return dataframe_parse_metadata


def get_parse_type_metadata():
    global parse_type_metadata
    return parse_type_metadata
