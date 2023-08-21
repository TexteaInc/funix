"""
Funix decorator. The central logic of Funix.
"""
from copy import deepcopy
from functools import wraps
from importlib import import_module
from inspect import Parameter, Signature, getsource, signature
from json import dumps
from secrets import token_hex
from traceback import format_exc
from types import ModuleType
from typing import Optional
from urllib.request import urlopen
from uuid import uuid4

from flask import Response, request, session

from funix.app import app
from funix.config import (
    banned_function_name_and_path,
    supported_basic_file_types,
    supported_basic_types,
    supported_basic_types_dict,
    supported_upload_widgets,
)
from funix.decorator.file import enable_file_service, get_static_uri
from funix.decorator.magic import (
    convert_row_item,
    function_param_to_widget,
    get_type_dict,
    get_type_widget_prop,
)
from funix.hint import (
    ArgumentConfigType,
    ConditionalVisibleType,
    DecoratedFunctionListItem,
    DestinationType,
    DirectionType,
    ExamplesType,
    InputLayout,
    LabelsType,
    OutputLayout,
    PreFillEmpty,
    PreFillType,
    TreatAsType,
    WhitelistType,
    WidgetsType,
)
from funix.session import get_global_variable, set_global_variable
from funix.theme import get_dict_theme, parse_theme
from funix.util.uri import is_valid_uri
from funix.widget import generate_frontend_widget_config

__matplotlib_use = False
"""
Whether Funix can handle matplotlib-related logic
"""

try:
    # From now on, Funix no longer mandates matplotlib and mpld3
    import matplotlib

    matplotlib.use("Agg")  # No display
    __matplotlib_use = True
except:
    pass


__decorated_functions_list: list[DecoratedFunctionListItem] = []
"""
A list, each element is a dict, record the information of the decorated function.

See `DecoratedFunctionListItem` for more information.
"""

__decorated_functions_names_list: list[str] = []
"""
A list, each element is the name of the decorated function.
"""

__decorated_secret_functions_dict: dict[str, str] = {}
"""
A dict, key is function id, value is secret.
For checking if the secret is correct.
"""

__decorated_id_to_function_dict: dict[str, str] = {}
"""
A dict, key is function id, value is function name.
"""

__wrapper_enabled: bool = False
"""
If the wrapper is enabled.
"""

__default_theme: dict = {}
"""
The default funix theme.
"""

__themes = {}
"""
A dict, key is theme name, value is funix theme.
"""

__parsed_themes = {}
"""
A dict, key is theme name, value is parsed MUI theme.
"""

__app_secret: str | None = None
"""
App secret, for all functions.
"""

mpld3: ModuleType | None = None
"""
The mpld3 module.
"""

pre_fill_metadata: dict[str, list[str | int | PreFillEmpty]] = {}
"""
A dict, key is function name, value is a list of indexes/keys of pre-fill parameters.
"""


def set_function_secret(secret: str, function_id: str, function_name: str) -> None:
    """
    Set the secret of a function.

    Parameters:
        secret (str): The secret.
        function_id (str): The function id.
        function_name (str): The function name.
    """
    global __decorated_secret_functions_dict, __decorated_id_to_function_dict
    __decorated_secret_functions_dict[function_id] = secret
    __decorated_id_to_function_dict[function_id] = function_name


def set_app_secret(secret: str) -> None:
    """
    Set the app secret, it will be used for all functions.

    Parameters:
        secret (str): The secret.
    """
    global __app_secret
    __app_secret = secret


def enable_wrapper() -> None:
    """
    Enable the wrapper, this will add the list and file path to the app.
    """
    global __wrapper_enabled, __decorated_functions_list
    if not __wrapper_enabled:
        __wrapper_enabled = True

        @app.get("/list")
        def __funix_export_func_list() -> dict:
            """
            Send the full function list.

            Routes:
                /list: The list path, we don't consider the GET "/" route, because it is the index page. And we start
                       frontend and backend at the same port.

            Returns:
                dict: The function list.
            """
            return {
                "list": __decorated_functions_list,
            }

        enable_file_service()


def set_default_theme(theme: str) -> None:
    """
    Set the default theme.

    Parameters:
        theme (str): The theme alias, path or url.
    """
    global __default_theme, __parsed_themes, __themes
    if theme in __themes:
        theme_dict = __themes[theme]
    else:
        if is_valid_uri(theme):
            theme_dict = get_dict_theme(None, theme)
        else:
            theme_dict = get_dict_theme(theme, None)
    __default_theme = theme_dict
    __parsed_themes["__default"] = parse_theme(__default_theme)


def set_theme(theme_dict: dict, alias: Optional[str] = None) -> None:
    """
    Set a theme from a dict.

    Parameters:
        theme_dict (dict): The theme dict.
        alias (str, optional): The theme alias.
    """
    global __themes
    name = theme_dict["name"]
    if alias is not None:
        name = alias
    __themes[name] = theme_dict


def import_theme(
    source: str,
    alias: Optional[str],
) -> None:
    """
    Import a theme from path, url.

    Parameters:
        source (str): The path or url of the theme.
        alias (str): The theme alias.

    Raises:
        ValueError: If the theme already exists.

    Notes:
        Check the `funix.theme.get_dict_theme` function for more information.
    """
    global __themes
    if is_valid_uri(source):
        theme = get_dict_theme(None, source)
    else:
        theme = get_dict_theme(source, None)
    name = theme["name"]
    if alias is not None:
        name = alias
    if name in __themes:
        raise ValueError(f"Theme {name} already exists")
    __themes[name] = theme


def clear_default_theme() -> None:
    """
    Clear the default theme.
    """
    global __default_theme, __parsed_themes
    __default_theme = {}
    __parsed_themes.pop("__default")


def export_secrets():
    """
    Export all secrets from the decorated functions.
    """
    __new_dict: dict[str, str] = {}
    for function_id, secret in __decorated_secret_functions_dict.items():
        __new_dict[__decorated_id_to_function_dict[function_id]] = secret
    return __new_dict


def funix(
    path: Optional[str] = None,
    title: Optional[str] = None,
    secret: bool | str = False,
    description: Optional[str] = "",
    destination: DestinationType = None,
    direction: DirectionType = None,
    show_source: bool = False,
    theme: Optional[str] = None,
    widgets: WidgetsType = None,
    treat_as: TreatAsType = None,
    whitelist: WhitelistType = None,
    examples: ExamplesType = None,
    argument_labels: LabelsType = None,
    input_layout: InputLayout = None,
    output_layout: OutputLayout = None,
    conditional_visible: ConditionalVisibleType = None,
    argument_config: ArgumentConfigType = None,
    pre_fill: PreFillType = None,
    __full_module: Optional[str] = None,
):
    """
    Decorator for functions to convert them to web apps
    The heart of Funix, all the beginning of the magic happens here
    (or at least most of it lol)

    See document for more details, the docstring here is just a brief summary

    Parameters:
        path(str): path to the function, if None, the function name will be used (if title available, use title)
        title(str): title of the function, if None, the function name will be used
        secret(bool|str):
            if False, the function will not be locked.
            if True, the function will be locked with a random 16 character password.
            if str, the function will be locked with the given password.
        description(str): description of the function, if None, the function docstring will be used
        destination(DestinationType): for yodas, no effect on funix
        direction(DirectionType): Whether the input/output panel is aligned left/right (row) or top/bottom (column)
        show_source(bool): whether to display the code of this function in the frontend
        theme(str): name, path or url of the theme to use, if None, the default theme will be used
        widgets(WidgetsType): parameters to be converted to widgets
        treat_as(TreatAsType): parameters to be treated as other types
        whitelist(WhitelistType): acceptable values for parameters
        examples(ExamplesType): examples for parameters
        argument_labels(LabelsType): labels for parameters
        input_layout(InputLayout): layout for input widgets
        output_layout(OutputLayout): layout for output widgets
        conditional_visible(ConditionalVisibleType): conditional visibility for widgets
        argument_config(ArgumentConfigType): config for widgets
        pre_fill(PreFillType): pre-fill values for parameters
        __full_module(str):
            full module path of the function, for `path` only.
            You don't need to set it unless you are funixing a directory and package.

    Returns:
        function: the decorated function

    Raises:
        Check code for details
    """
    global __parsed_themes, pre_fill_metadata

    def decorator(function: callable) -> callable:
        """
        Decorator for functions to convert them to web apps

        Parameters:
            function(callable): the function to be decorated

        Returns:
            callable: the decorated function

        Raises:
            Check code for details
        """
        if __wrapper_enabled:
            function_id = str(uuid4())

            function_direction = direction if direction else "row"

            function_name = getattr(
                function, "__name__"
            )  # function name as id to retrieve function info
            if function_name in banned_function_name_and_path:
                raise ValueError(
                    f"{function_name} is not allowed, banned names: {banned_function_name_and_path}"
                )

            function_title = title if title is not None else function_name

            function_description = description
            if function_description is None:
                if function_docstring := getattr(function, "__doc__"):
                    function_description = function_docstring

            if not theme:
                if "__default" in __parsed_themes:
                    parsed_theme = __parsed_themes["__default"]
                else:
                    parsed_theme = [], {}, {}, {}, {}
            else:
                if theme in __parsed_themes:
                    parsed_theme = __parsed_themes[theme]
                else:
                    # Cache
                    if theme in __themes:
                        parsed_theme = parse_theme(__themes[theme])
                        __parsed_themes[theme] = parsed_theme
                    else:
                        import_theme(theme, alias=theme)  # alias is not important here
                        parsed_theme = parse_theme(__themes[theme])
                        __parsed_themes[theme] = parsed_theme

            if not path:
                endpoint = function_name
            else:
                if path in banned_function_name_and_path:
                    raise Exception(f"{function_name}'s path: {path} is not allowed")
                endpoint = path.strip("/")

            if function_title in __decorated_functions_names_list:
                raise ValueError(f"Function with name {function_title} already exists")

            if __app_secret is not None:
                set_function_secret(__app_secret, function_id, function_title)
            elif secret:
                if isinstance(secret, bool):
                    set_function_secret(token_hex(16), function_id, function_title)
                else:
                    set_function_secret(secret, function_id, function_title)

            secret_key = __decorated_secret_functions_dict.get(function_id, None)

            __decorated_functions_names_list.append(function_title)
            __decorated_functions_list.append(
                {
                    "name": function_title,
                    "path": endpoint,
                    "module": __full_module,
                    "secret": secret_key,
                }
            )

            if show_source:
                source_code = getsource(function)
            else:
                source_code = ""

            function_signature = signature(function)
            function_params = function_signature.parameters
            decorated_params = {}
            json_schema_props = {}

            cast_to_list_flag = False

            if function_signature.return_annotation is not Signature.empty:
                # TODO: Magic code, I've forgotten what it does, but it works, refactor it if you can
                # return type dict enforcement for yodas only
                try:
                    if (
                        cast_to_list_flag := function_signature.return_annotation.__class__.__name__
                        == "tuple"
                        or function_signature.return_annotation.__name__ == "Tuple"
                    ):
                        parsed_return_annotation_list = []
                        return_annotation = list(
                            function_signature.return_annotation
                            if function_signature.return_annotation.__class__.__name__
                            == "tuple"
                            else function_signature.return_annotation.__args__
                        )
                        for return_annotation_type in return_annotation:
                            return_annotation_type_name = getattr(
                                return_annotation_type, "__name__"
                            )
                            if return_annotation_type_name in supported_basic_types:
                                return_annotation_type_name = (
                                    supported_basic_types_dict[
                                        return_annotation_type_name
                                    ]
                                )
                            elif return_annotation_type_name == "List":
                                list_type_name = getattr(
                                    getattr(return_annotation_type, "__args__")[0],
                                    "__name__",
                                )
                                if list_type_name in supported_basic_file_types:
                                    return_annotation_type_name = list_type_name
                            parsed_return_annotation_list.append(
                                return_annotation_type_name
                            )
                        return_type_parsed = parsed_return_annotation_list
                    else:
                        if hasattr(
                            function_signature.return_annotation, "__annotations__"
                        ):
                            return_type_raw = getattr(
                                function_signature.return_annotation, "__annotations__"
                            )
                            if getattr(type(return_type_raw), "__name__") == "dict":
                                if (
                                    function_signature.return_annotation.__name__
                                    == "Figure"
                                ):
                                    return_type_parsed = "Figure"
                                else:
                                    return_type_parsed = {}
                                    for (
                                        return_type_key,
                                        return_type_value,
                                    ) in return_type_raw.items():
                                        return_type_parsed[return_type_key] = str(
                                            return_type_value
                                        )
                            else:
                                return_type_parsed = str(return_type_raw)
                        else:
                            return_type_parsed = getattr(
                                function_signature.return_annotation, "__name__"
                            )
                            if return_type_parsed in supported_basic_types:
                                return_type_parsed = supported_basic_types_dict[
                                    return_type_parsed
                                ]
                            elif return_type_parsed == "List":
                                list_type_name = getattr(
                                    getattr(
                                        function_signature.return_annotation, "__args__"
                                    )[0],
                                    "__name__",
                                )
                                if list_type_name in supported_basic_file_types:
                                    return_type_parsed = list_type_name
                except:
                    return_type_parsed = get_type_dict(
                        function_signature.return_annotation
                    )
                    if return_type_parsed is not None:
                        return_type_parsed = return_type_parsed["type"]
            else:
                return_type_parsed = None

            return_input_layout = []

            safe_input_layout = [] if not input_layout else input_layout

            for row in safe_input_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    for common_row_item_key in ["markdown", "html"]:
                        if common_row_item_key in row_item:
                            row_item_done = convert_row_item(
                                row_item, common_row_item_key
                            )
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

            safe_output_layout = [] if not output_layout else output_layout

            for row in safe_output_layout:
                row_layout = []
                for row_item in row:
                    row_item_done = row_item
                    for common_row_item_key in [
                        "markdown",
                        "html",
                        "images",
                        "videos",
                        "audios",
                        "files",
                    ]:
                        if common_row_item_key in row_item:
                            row_item_done = convert_row_item(
                                row_item, common_row_item_key
                            )
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
                    elif "index" in row_item:
                        row_item_done["type"] = "index"
                        return_output_indexes.append(row_item_done["index"])
                    row_layout.append(row_item_done)
                return_output_layout.append(row_layout)

            if pre_fill:
                for _, from_arg_function_info in pre_fill.items():
                    if isinstance(from_arg_function_info, tuple):
                        from_arg_function_name = getattr(
                            from_arg_function_info[0], "__name__"
                        )
                        from_arg_function_index_or_key = from_arg_function_info[1]
                        if from_arg_function_name in pre_fill_metadata:
                            pre_fill_metadata[from_arg_function_name].append(
                                from_arg_function_index_or_key
                            )
                        else:
                            pre_fill_metadata[from_arg_function_name] = [
                                from_arg_function_index_or_key
                            ]
                    else:
                        from_arg_function_name = getattr(
                            from_arg_function_info, "__name__"
                        )
                        if from_arg_function_name in pre_fill_metadata:
                            pre_fill_metadata[from_arg_function_name].append(
                                PreFillEmpty
                            )
                        else:
                            pre_fill_metadata[from_arg_function_name] = [PreFillEmpty]

            def create_decorated_params(arg_name: str) -> None:
                """
                Creates a decorated_params entry for the given arg_name if it doesn't exist

                Parameters:
                    arg_name (str): The name of the argument
                """
                if arg_name not in decorated_params:
                    decorated_params[arg_name] = {}

            def put_props_in_params(
                arg_name: str, prop_name: str, prop_value: any
            ) -> None:
                """
                Puts the given prop_name and prop_value in the decorated_params entry for the given arg_name

                Parameters:
                    arg_name (str): The name of the argument
                    prop_name (str): The name of the prop
                    prop_value (any): The value of the prop
                """
                create_decorated_params(arg_name)
                decorated_params[arg_name][prop_name] = prop_value

            def check_example_whitelist(arg_name: str) -> None:
                """
                Checks if the given arg_name has both an example and a whitelist

                Parameters:
                    arg_name (str): The name of the argument

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

            def parse_widget(widget_info: str | tuple | list) -> list[str] | str:
                """
                Parses the given widget_info

                Parameters:
                    widget_info (str | tuple | list): The widget_info to parse

                Returns:
                    list[str] | str: The widget
                """
                if isinstance(widget_info, str):
                    return widget_info
                elif isinstance(widget_info, tuple):
                    return generate_frontend_widget_config(widget_info)
                elif isinstance(widget_info, list):
                    widget_result = []
                    for widget_item in widget_info:
                        if isinstance(widget_item, tuple):
                            widget_result.append(
                                generate_frontend_widget_config(widget_item)
                            )
                        elif isinstance(widget_item, list):
                            widget_result.append(parse_widget(widget_item))
                        elif isinstance(widget_item, str):
                            widget_result.append(widget_item)
                    return widget_result

            safe_widgets = {} if not widgets else widgets
            safe_treat_as = {} if not treat_as else treat_as
            safe_examples = {} if not examples else examples
            safe_whitelist = {} if not whitelist else whitelist
            safe_argument_labels = {} if not argument_labels else argument_labels

            for prop in [
                [safe_widgets, "widget"],
                [safe_treat_as, "treat_as"],
                [safe_argument_labels, "title"],
                [safe_examples, "example"],
                [safe_whitelist, "whitelist"],
            ]:
                for prop_arg_name in prop[0]:
                    if isinstance(prop_arg_name, str):
                        if prop[1] == "widget":
                            put_props_in_params(
                                prop_arg_name,
                                prop[1],
                                parse_widget(prop[0][prop_arg_name]),
                            )
                        else:
                            put_props_in_params(
                                prop_arg_name, prop[1], prop[0][prop_arg_name]
                            )
                        if prop[1] in ["example", "whitelist"]:
                            check_example_whitelist(prop_arg_name)
                    else:
                        if prop[1] in ["example", "whitelist"]:
                            for index, single_prop_arg_name in enumerate(prop_arg_name):
                                put_props_in_params(
                                    single_prop_arg_name,
                                    prop[1],
                                    prop[0][single_prop_arg_name][index],
                                )
                                check_example_whitelist(single_prop_arg_name)
                        elif prop[1] == "widget":
                            cached_result = parse_widget(prop[0][prop_arg_name])
                            for prop_arg_name_item in prop_arg_name:
                                put_props_in_params(
                                    prop_arg_name_item, prop[1], cached_result
                                )
                        else:
                            for prop_arg_name_item in prop_arg_name:
                                put_props_in_params(
                                    prop_arg_name_item, prop[1], prop[0][prop_arg_name]
                                )
            input_attr = ""

            safe_argument_config = {} if argument_config is None else argument_config

            for decorator_arg_name, decorator_arg_dict in safe_argument_config.items():
                if isinstance(decorator_arg_name, str):
                    decorator_arg_names = [decorator_arg_name]
                else:
                    decorator_arg_names = list(decorator_arg_name)
                for single_decorator_arg_name in decorator_arg_names:
                    if single_decorator_arg_name not in decorated_params:
                        decorated_params[single_decorator_arg_name] = {}

                    treat_as_config = decorator_arg_dict.get("treat_as", "config")
                    decorated_params[single_decorator_arg_name][
                        "treat_as"
                    ] = treat_as_config
                    if treat_as_config != "config":
                        input_attr = (
                            decorator_arg_dict["treat_as"]
                            if input_attr == ""
                            else input_attr
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

            for _, function_param in function_params.items():
                function_arg_name = function_param.name
                decorated_params[function_arg_name] = decorated_params.get(
                    function_arg_name, {}
                )
                decorated_params[function_arg_name]["treat_as"] = decorated_params[
                    function_arg_name
                ].get("treat_as", "config")

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
                if "widget" in decorated_params[function_arg_name]:
                    widget = decorated_params[function_arg_name]["widget"]
                else:
                    if function_arg_type_dict is None:
                        widget = "json"
                    else:
                        if function_arg_type_dict["type"] in [
                            "list",
                            "dict",
                            "typing.Dict",
                        ]:
                            widget = "json"
                        else:
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
                    {}
                    if "widget" in decorated_params[function_arg_name]
                    else parsed_theme[1],
                    function_param.annotation,
                )

                for prop_key in ["whitelist", "example", "keys", "default", "title"]:
                    if prop_key in decorated_params[function_arg_name].keys():
                        json_schema_props[function_arg_name][
                            prop_key
                        ] = decorated_params[function_arg_name][prop_key]

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
                    json_schema_props[function_arg_name][
                        "items"
                    ] = get_type_widget_prop(
                        param_type,
                        0,
                        widget[1:],
                        {}
                        if "widget" in decorated_params[function_arg_name]
                        else parsed_theme[1],
                        function_param.annotation,
                    )
                    json_schema_props[function_arg_name]["type"] = "array"

            all_of = []
            delete_keys = set()
            safe_conditional_visible = (
                {} if conditional_visible is None else conditional_visible
            )

            for conditional_visible_item in safe_conditional_visible:
                config = {
                    "if": {"properties": {}},
                    "then": {"properties": {}},
                    "required": [],
                }
                if_items: any = conditional_visible_item["when"]
                then_items = conditional_visible_item["show"]
                for if_item in if_items.keys():
                    config["if"]["properties"][if_item] = {"const": if_items[if_item]}
                for then_item in then_items:
                    config["then"]["properties"][then_item] = json_schema_props[
                        then_item
                    ]
                    config["required"].append(then_item)
                    delete_keys.add(then_item)
                all_of.append(config)

            for key in delete_keys:
                json_schema_props.pop(key)

            decorated_function = {
                "id": function_id,
                "name": function_name,
                "params": decorated_params,
                "theme": parsed_theme[4],
                "return_type": return_type_parsed,
                "description": function_description,
                "direction": function_direction,
                "schema": {
                    "title": function_title,
                    "description": function_description,
                    "type": "object",
                    "properties": json_schema_props,
                    "allOf": all_of,
                    "input_layout": return_input_layout,
                    "output_layout": return_output_layout,
                    "output_indexes": return_output_indexes,
                },
                "destination": destination,
                "source": source_code,
            }

            get_wrapper_endpoint = app.get(f"/param/{endpoint}")
            get_wrapper_id = app.get(f"/param/{function_id}")

            def decorated_function_param_getter():
                """
                Returns the function's parameters

                Routes:
                    /param/{endpoint}
                    /param/{function_id}

                Returns:
                    flask.Response: The function's parameters
                """
                if pre_fill is not None:
                    new_decorated_function = deepcopy(decorated_function)
                    for argument_key, from_function_info in pre_fill.items():
                        if isinstance(from_function_info, tuple):
                            last_result = get_global_variable(
                                getattr(from_function_info[0], "__name__")
                                + f"_{from_function_info[1]}"
                            )
                        else:
                            last_result = get_global_variable(
                                getattr(from_function_info, "__name__") + "_result"
                            )
                        if last_result is not None:
                            new_decorated_function["params"][argument_key][
                                "default"
                            ] = last_result
                            new_decorated_function["schema"]["properties"][
                                argument_key
                            ]["default"] = last_result
                    return Response(
                        dumps(new_decorated_function), mimetype="application/json"
                    )
                return Response(dumps(decorated_function), mimetype="application/json")

            decorated_function_param_getter.__setattr__(
                "__name__", f"{function_name}_param_getter"
            )
            get_wrapper_endpoint(decorated_function_param_getter)
            get_wrapper_id(decorated_function_param_getter)

            if secret_key:
                verify_secret_endpoint = app.post(f"/verify/{endpoint}")
                verify_secret_id = app.post(f"/verify/{function_id}")

                def verify_secret():
                    """
                    Verifies the user's secret

                    Routes:
                        /verify/{endpoint}
                        /verify/{function_id}

                    Returns:
                        flask.Response: The verification result
                    """
                    data = request.get_json()

                    failed_data = Response(
                        dumps(
                            {
                                "success": False,
                            }
                        ),
                        mimetype="application/json",
                        status=400,
                    )

                    if data is None:
                        return failed_data

                    if "secret" not in data:
                        return failed_data

                    user_secret = request.get_json()["secret"]
                    if user_secret == __decorated_secret_functions_dict[function_id]:
                        return Response(
                            dumps(
                                {
                                    "success": True,
                                }
                            ),
                            mimetype="application/json",
                            status=200,
                        )
                    else:
                        return failed_data

                verify_secret.__setattr__("__name__", f"{function_name}_verify_secret")
                verify_secret_endpoint(verify_secret)
                verify_secret_id(verify_secret)

            @wraps(function)
            def wrapper():
                """
                The function's wrapper

                Routes:
                    /call/{endpoint}
                    /call/{function_id}

                Returns:
                    Any: The function's result
                """
                try:
                    if not session.get("__funix_id"):
                        session["__funix_id"] = uuid4().hex
                    function_kwargs = request.get_json()

                    def get_figure(figure) -> dict:
                        """
                        Converts a matplotlib figure to a dictionary for drawing on the frontend

                        Parameters:
                            figure (matplotlib.figure.Figure): The figure to convert

                        Returns:
                            dict: The converted figure

                        Raises:
                            Exception: If matplotlib or mpld3 is not installed
                        """
                        global mpld3
                        if __matplotlib_use:
                            if mpld3 is None:
                                try:
                                    import matplotlib.pyplot

                                    mpld3 = import_module("mpld3")
                                except:
                                    raise Exception(
                                        "if you use matplotlib, you must install mpld3"
                                    )
                            else:
                                fig = mpld3.fig_to_dict(figure)
                                fig["width"] = 560  # TODO: Change it in frontend
                                return fig
                        else:
                            raise Exception("Install matplotlib to use this function")

                    @wraps(function)
                    def wrapped_function(**wrapped_function_kwargs):
                        """
                        The function's wrapper
                        """
                        # TODO: Best result handling, refactor it if possible
                        try:
                            function_call_result = function(**wrapped_function_kwargs)
                            function_call_name = getattr(function, "__name__")
                            if function_call_name in pre_fill_metadata:
                                for index_or_key in pre_fill_metadata[
                                    function_call_name
                                ]:
                                    if index_or_key is PreFillEmpty:
                                        set_global_variable(
                                            function_call_name + "_result",
                                            function_call_result,
                                        )
                                    else:
                                        set_global_variable(
                                            function_call_name + f"_{index_or_key}",
                                            function_call_result[index_or_key],
                                        )
                            if return_type_parsed == "Figure":
                                return [get_figure(function_call_result)]
                            if return_type_parsed in supported_basic_file_types:
                                return [get_static_uri(function_call_result)]
                            else:
                                if isinstance(function_call_result, list):
                                    return [function_call_result]
                                if not isinstance(
                                    function_call_result, (str, dict, tuple)
                                ):
                                    function_call_result = dumps(function_call_result)
                                if cast_to_list_flag:
                                    function_call_result = list(function_call_result)
                                else:
                                    if isinstance(function_call_result, (str, dict)):
                                        function_call_result = [function_call_result]
                                    if isinstance(function_call_result, tuple):
                                        function_call_result = list(
                                            function_call_result
                                        )
                                if function_call_result and isinstance(
                                    function_call_result, list
                                ):
                                    if isinstance(return_type_parsed, list):
                                        for position, single_return_type in enumerate(
                                            return_type_parsed
                                        ):
                                            if single_return_type == "Figure":
                                                function_call_result[
                                                    position
                                                ] = get_figure(
                                                    function_call_result[position]
                                                )
                                            if (
                                                single_return_type
                                                in supported_basic_file_types
                                            ):
                                                if (
                                                    type(function_call_result[position])
                                                    == "list"
                                                ):
                                                    function_call_result[position] = [
                                                        get_static_uri(single)
                                                        for single in function_call_result[
                                                            position
                                                        ]
                                                    ]
                                                else:
                                                    function_call_result[
                                                        position
                                                    ] = get_static_uri(
                                                        function_call_result[position]
                                                    )
                                        return function_call_result
                                    else:
                                        if return_type_parsed == "Figure":
                                            function_call_result = [
                                                get_figure(function_call_result[0])
                                            ]
                                        if (
                                            return_type_parsed
                                            in supported_basic_file_types
                                        ):
                                            if type(function_call_result[0]) == "list":
                                                function_call_result = [
                                                    [
                                                        get_static_uri(single)
                                                        for single in function_call_result[
                                                            0
                                                        ]
                                                    ]
                                                ]
                                            else:
                                                function_call_result = [
                                                    get_static_uri(
                                                        function_call_result[0]
                                                    )
                                                ]
                                        return function_call_result
                                return function_call_result
                        except:
                            return {
                                "error_type": "function",
                                "error_body": format_exc(),
                            }

                    cell_names = []
                    upload_base64_files = {}

                    # TODO: And the logic below, refactor it if possible

                    for json_schema_prop_key in json_schema_props.keys():
                        if "treat_as" in json_schema_props[json_schema_prop_key]:
                            if (
                                json_schema_props[json_schema_prop_key]["treat_as"]
                                == "cell"
                            ):
                                cell_names.append(json_schema_prop_key)
                        if "widget" in json_schema_props[json_schema_prop_key]:
                            if (
                                json_schema_props[json_schema_prop_key]["widget"]
                                in supported_upload_widgets
                            ):
                                upload_base64_files[json_schema_prop_key] = "single"
                        if "items" in json_schema_props[json_schema_prop_key]:
                            if (
                                "widget"
                                in json_schema_props[json_schema_prop_key]["items"]
                            ):
                                if (
                                    json_schema_props[json_schema_prop_key]["items"][
                                        "widget"
                                    ]
                                    in supported_upload_widgets
                                ):
                                    upload_base64_files[
                                        json_schema_prop_key
                                    ] = "multiple"

                    if function_kwargs is None:
                        return {
                            "error_type": "wrapper",
                            "error_body": "No arguments passed to function.",
                        }
                    if secret_key:
                        if "__funix_secret" in function_kwargs:
                            if (
                                not __decorated_secret_functions_dict[function_id]
                                == function_kwargs["__funix_secret"]
                            ):
                                return {
                                    "error_type": "wrapper",
                                    "error_body": "Provided secret is incorrect.",
                                }
                            else:
                                del function_kwargs["__funix_secret"]
                        else:
                            return {
                                "error_type": "wrapper",
                                "error_body": "No secret provided.",
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
                        for upload_base64_file_key in upload_base64_files.keys():
                            if upload_base64_files[upload_base64_file_key] == "single":
                                with urlopen(
                                    function_kwargs[upload_base64_file_key]
                                ) as rsp:
                                    new_args[upload_base64_file_key] = rsp.read()
                            elif (
                                upload_base64_files[upload_base64_file_key]
                                == "multiple"
                            ):
                                for pos, each in enumerate(
                                    function_kwargs[upload_base64_file_key]
                                ):
                                    with urlopen(each) as rsp:
                                        new_args[upload_base64_file_key][
                                            pos
                                        ] = rsp.read()
                        return wrapped_function(**new_args)
                    else:
                        return wrapped_function(**function_kwargs)
                except:
                    return {"error_type": "wrapper", "error_body": format_exc()}

            post_wrapper = app.post(f"/call/{function_id}")
            post_wrapper(wrapper)
            post_wrapper = app.post(f"/call/{endpoint}")
            post_wrapper(wrapper)
            wrapper._decorator_name_ = "funix"
        return function

    return decorator
