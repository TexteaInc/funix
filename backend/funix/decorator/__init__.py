"""
Funix decorator. The central logic of Funix.
"""
import ast
import inspect
import sys
from copy import deepcopy
from functools import wraps
from importlib import import_module
from inspect import Parameter, getsource, isgeneratorfunction, signature
from json import dumps, loads
from secrets import token_hex
from traceback import format_exc
from types import ModuleType
from typing import Any, Callable, Optional, Union
from urllib.request import urlopen
from uuid import uuid4

from flask import Response, request, session
from funix.decorator.layout import handle_input_layout, handle_output_layout
from funix.decorator.magic import (
    parse_function_annotation,
    get_type_widget_prop,
    get_type_dict,
    anal_function_result,
    function_param_to_widget,
)
from funix.decorator.pre_fill import parse_pre_fill, get_pre_fill_metadata
from funix.decorator.widget import widget_parse, parse_widget
from requests import post

from funix.app import app, sock
from funix.app.websocket import StdoutToWebsocket
from funix.config import (
    banned_function_name_and_path,
    supported_upload_widgets,
)
from funix.config.switch import GlobalSwitchOption
from funix.decorator.annnotation_analyzer import (
    analyze,
    register_ipywidgets,
    register_pandera,
)
from funix.decorator.file import (
    enable_file_service,
    get_static_uri,
    handle_ipython_audio_image_video,
)
from funix.decorator.limit import Limiter, global_rate_limiters, parse_limiter_args
from funix.decorator.lists import (
    decorated_functions_list_append,
    enable_list,
    get_default_function_name,
    push_counter,
    set_default_function,
)
from funix.decorator.reactive import function_reactive_update, get_reactive_config
from funix.decorator.runtime import RuntimeClassVisitor
from funix.decorator.theme import (
    get_parsed_theme_fot_funix,
    import_theme,
    parsed_themes,
    themes,
)
from funix.hint import (
    ArgumentConfigType,
    ConditionalVisibleType,
    DestinationType,
    DirectionType,
    ExamplesType,
    InputLayout,
    LabelsType,
    Markdown,
    OutputLayout,
    PreFillEmpty,
    PreFillType,
    ReactiveType,
    TreatAsType,
    WhitelistType,
    WidgetsType,
    WrapperException,
)
from funix.session import get_global_variable, set_global_variable
from funix.util.module import funix_menu_to_safe_function_name
from funix.util.text import un_indent
from funix.util.uri import get_endpoint

__ipywidgets_use = False
"""
Whether Funix can handle ipywidgets-related logic
"""

try:
    register_ipywidgets()

    __ipywidgets_use = True
except:
    pass


__pandas_use = False
"""
Whether Funix can handle pandas or pandera-related logic
"""

__pandas_module: None | ModuleType = None
__pandera_module: None | ModuleType = None

try:
    __pandas_module = import_module("pandas")
    __pandera_module = import_module("pandera")

    register_pandera()

    __pandas_use = True
except:
    pass

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

__app_secret: str | None = None
"""
App secret, for all functions.
"""

parse_type_metadata: dict[str, dict[str, Any]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""

dataframe_parse_metadata: dict[str, dict[str, list[str]]] = {}
"""
A dict, key is function ID, value is a map of parameter name to type.
"""

now_module: str | None = None
"""
External passes to module, recorded here, are used to help funix decoration override config.
"""


kumo_callback_url: str | None = None
"""
Kumo callback url. For kumo only, only record the call numbers.
"""

kumo_callback_token: str | None = None
"""
Kumo callback token.
"""

dir_mode_default_info: tuple[bool, str | None] = (False, None)
"""
Default dir mode info.
"""

handled_object: list[int] = []
"""
Handled object ids.
"""

class_method_ids_to_params: dict[int, dict] = {}
"""
Class method ids to params.
"""


def funix_method(*args, **kwargs):
    def decorator(func):
        class_method_ids_to_params[id(func)] = {
            "args": args,
            "kwargs": kwargs,
        }
        return func

    return decorator


def set_kumo_info(url: str, token: str) -> None:
    """
    Set the kumo info.

    Parameters:
        url (str): The url.
        token (str): The token.
    """
    global kumo_callback_url, kumo_callback_token
    kumo_callback_url = url
    kumo_callback_token = token


def set_function_secret(secret: str, function_id: str, function_name: str) -> None:
    """
    Set the secret of a function.

    Parameters:
        secret (str): The secret.
        function_id (str): The function id.
        function_name (str): The function name (or with path).
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


def set_now_module(module: str) -> None:
    """
    Set the now module.

    Parameters:
        module (str): The module.
    """
    global now_module
    now_module = module


def clear_now_module() -> None:
    """
    Clear the now module.
    """
    global now_module
    now_module = None


def set_dir_mode_default_info(info: tuple[bool, str | None]) -> None:
    """
    Set this function as default.
    """
    global dir_mode_default_info
    dir_mode_default_info = info


def enable_wrapper() -> None:
    """
    Enable the wrapper, this will add the list and file path to the app.
    """
    global __wrapper_enabled
    if not __wrapper_enabled:
        __wrapper_enabled = True

        enable_list()
        enable_file_service()


def object_is_handled(object_id: int) -> bool:
    """
    Check if the object is handled.

    Parameters:
        object_id (int): The object id.

    Returns:
        bool: True if handled, False otherwise.
    """
    return object_id in handled_object


def export_secrets():
    """
    Export all secrets from the decorated functions.
    """
    __new_dict: dict[str, str] = {}
    for function_id, secret in __decorated_secret_functions_dict.items():
        __new_dict[__decorated_id_to_function_dict[function_id]] = secret
    return __new_dict


def kumo_callback():
    """
    Kumo callback.
    """
    global kumo_callback_url, kumo_callback_token
    if kumo_callback_url and kumo_callback_token:
        try:
            post(
                kumo_callback_url,
                json={
                    "token": kumo_callback_token,
                },
                timeout=1,
            )
        except:
            pass


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
    menu: Optional[str] = None,
    default: bool = False,
    rate_limit: Union[Limiter, list, dict, None] = None,
    reactive: ReactiveType = None,
    print_to_web: bool = False,
    autorun: bool = False,
    disable: bool = False,
    figure_to_image: bool = False,
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
        menu(str):
            full module path of the function, for `path` only.
            You don't need to set it unless you are funixing a directory and package.
        default(bool): whether this function is the default function
        rate_limit(Limiter | list[Limiter]): rate limiters, an object or a list
        reactive(ReactiveType): reactive config
        print_to_web(bool): handle all stdout to web
        autorun(bool): allow users to use continuity runs on the front end
        disable(bool): disable this function
        figure_to_image(bool): convert matplotlib figure to image

    Returns:
        function: the decorated function

    Raises:
        Check code for details
    """
    global parse_type_metadata

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
        handled_object.append(id(function))
        if disable:
            return function
        if __wrapper_enabled:
            if menu:
                push_counter(menu)
            elif now_module:
                push_counter(now_module)
            else:
                push_counter("$Funix_Main")

            function_id = str(uuid4())

            if default:
                set_default_function(function_id)

            safe_module_now = now_module

            if safe_module_now:
                safe_module_now = funix_menu_to_safe_function_name(safe_module_now)

            parse_type_metadata[function_id] = {}

            function_direction = direction if direction else "row"

            function_name = getattr(function, "__name__")
            """
            function name as id to retrieve function info
            now don't use function name as id, use function id instead

            Rest In Peace: f765733; Jul 9, 2022 - Oct 23, 2023
            """

            if dir_mode_default_info[0]:
                if function_name == dir_mode_default_info[1]:
                    set_default_function(function_id)
            elif default_function_name_ := get_default_function_name():
                if function_name == default_function_name_:
                    set_default_function(function_id)

            unique_function_name: str | None = None  # Don't use it as id,
            # only when funix starts with `-R`, it will be not None

            if safe_module_now:
                unique_function_name = (
                    now_module.replace(".", "/") + "/" + function_name
                )

            if function_name in banned_function_name_and_path:
                raise ValueError(
                    f"{function_name} is not allowed, banned names: {banned_function_name_and_path}"
                )

            function_name_ = function_name

            if GlobalSwitchOption.AUTO_CONVERT_UNDERSCORE_TO_SPACE_IN_NAME:
                function_name_ = function_name_.replace("_", " ")

            function_title = title if title is not None else function_name_

            function_description = description
            if function_description == "" or function_description is None:
                if GlobalSwitchOption.AUTO_READ_DOCSTRING_TO_FUNCTION_DESCRIPTION:
                    function_docstring = getattr(function, "__doc__")
                    if function_docstring:
                        function_description = un_indent(function_docstring)

            parsed_theme = get_parsed_theme_fot_funix(theme)

            endpoint = get_endpoint(path, unique_function_name, function_name)

            if unique_function_name:
                if unique_function_name in __decorated_functions_names_list:
                    raise ValueError(
                        f"Function with name {function_name} already exists, you better check other files, they may "
                        f"have the same function name"
                    )
            else:
                if function_title in __decorated_functions_names_list:
                    raise ValueError(
                        f"Function with name {function_title} already exists"
                    )

            if __app_secret is not None:
                set_function_secret(__app_secret, function_id, function_title)
            elif secret:
                if isinstance(secret, bool):
                    set_function_secret(token_hex(16), function_id, function_title)
                else:
                    set_function_secret(secret, function_id, function_title)

            secret_key = __decorated_secret_functions_dict.get(function_id, None)

            replace_module = None

            if now_module:
                replace_module = now_module

            if menu:
                replace_module = menu

            if unique_function_name:
                __decorated_functions_names_list.append(unique_function_name)
            else:
                __decorated_functions_names_list.append(function_title)

            need_websocket = isgeneratorfunction(function)

            function_signature = signature(function)
            function_params = function_signature.parameters

            if print_to_web:
                print(
                    f"WARNING: the {function_name} function turn on the `print_to_web` option, "
                    f"the return annotation will be forced to be `markdown`, and the websocket mode is forced to be on."
                )
                need_websocket = True
                setattr(function_signature, "_return_annotation", Markdown)

            has_reactive_params = False

            reactive_config: dict[str, tuple[Callable, dict[str, str]]] = {}
            """
            Empty dict: full form data
            Dict argument keys: map
            """

            if isinstance(reactive, dict):
                has_reactive_params = True
                reactive_config = get_reactive_config(
                    reactive, function_params, function_name
                )

                def _function_reactive_update():
                    return function_reactive_update(reactive_config)

                _function_reactive_update.__name__ = function_name + "_reactive_update"

                if safe_module_now:
                    _function_reactive_update.__name__ = (
                        f"{safe_module_now}_{_function_reactive_update.__name__}"
                    )

                app.post(f"/update/{function_id}")(_function_reactive_update)
                app.post(f"/update/{endpoint}")(_function_reactive_update)

            decorated_functions_list_append(
                {
                    "name": function_title,
                    "path": endpoint,
                    "module": replace_module,
                    "secret": secret_key,
                    "id": function_id,
                    "websocket": need_websocket,
                    "reactive": has_reactive_params,
                    "autorun": autorun,
                }
            )

            if show_source:
                source_code = getsource(function)
            else:
                source_code = ""

            decorated_params = {}
            json_schema_props = {}

            cast_to_list_flag, return_type_parsed = parse_function_annotation(
                function_signature, figure_to_image
            )

            safe_input_layout = [] if not input_layout else input_layout
            return_input_layout, _need_update = handle_input_layout(safe_input_layout)

            decorated_params.update(_need_update)

            safe_output_layout = [] if not output_layout else output_layout

            return_output_layout, return_output_indexes = handle_output_layout(
                safe_output_layout
            )

            if pre_fill:
                parse_pre_fill(pre_fill)

            widget_parse(
                function_params,
                decorated_params,
                function_name,
                widgets,
                argument_labels,
                treat_as,
                examples,
                whitelist,
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
                if __pandas_use:
                    anno = function_param.annotation
                    default_values = (
                        {}
                        if function_param.default is Parameter.empty
                        else function_param.default
                    )

                    def analyze_columns_and_default_value(pandas_like_anno):
                        column_names = []
                        dataframe_parse_metadata[
                            function_id
                        ] = dataframe_parse_metadata.get(function_id, {})
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

                    if isinstance(anno, __pandas_module.DataFrame):
                        if anno.columns.size == 0:
                            raise Exception(
                                f"{function_name}: pandas.DataFrame() is not supported, "
                                f"but you can add columns to it, if you mean DataFrame with no columns, "
                                f"please use `pandas.DataFrame` instead."
                            )
                        else:
                            analyze_columns_and_default_value(anno)
                            continue

                    if anno is __pandas_module.core.frame.DataFrame:
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
                        is __pandera_module.typing.pandas.DataFrame
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
                            "list",
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
                    {}
                    if "widget" in decorated_params[function_arg_name]
                    else theme_widgets,
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
                        else theme_widgets,
                        function_param.annotation,
                    )
                    json_schema_props[function_arg_name]["type"] = "array"

                if custom_component is not None:
                    json_schema_props[function_arg_name][
                        "funixComponent"
                    ] = custom_component
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
                if_items: Any = conditional_visible_item["when"]
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

            get_wrapper_id = app.get(f"/param/{function_id}")
            get_wrapper_endpoint = app.get(f"/param/{endpoint}")

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
                                str(id(from_function_info[0]))
                                + f"_{from_function_info[1]}"
                            )
                        else:
                            last_result = get_global_variable(
                                str(id(from_function_info)) + "_result"
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

            decorated_function_param_getter_name = f"{function_name}_param_getter"

            if safe_module_now:
                decorated_function_param_getter_name = (
                    f"{safe_module_now}_{decorated_function_param_getter_name}"
                )

            decorated_function_param_getter.__setattr__(
                "__name__", f"{decorated_function_param_getter_name}"
            )

            get_wrapper_id(decorated_function_param_getter)
            get_wrapper_endpoint(decorated_function_param_getter)

            if secret_key:
                verify_secret_id = app.post(f"/verify/{function_id}")
                verify_secret_endpoint = app.post(f"/verify/{endpoint}")

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

                decorated_function_verify_secret_name = f"{function_name}_verify_secret"

                if safe_module_now:
                    decorated_function_verify_secret_name = (
                        f"{safe_module_now}_{decorated_function_verify_secret_name}"
                    )

                verify_secret.__setattr__(
                    "__name__", decorated_function_verify_secret_name
                )

                verify_secret_endpoint(verify_secret)
                verify_secret_id(verify_secret)

            limiters = parse_limiter_args(rate_limit)

            @wraps(function)
            def wrapper(ws=None):
                """
                The function's wrapper

                Routes:
                    /call/{endpoint}
                    /call/{function_id}

                Returns:
                    Any: The function's result
                """

                for limiter in global_rate_limiters + limiters:
                    limit_result = limiter.rate_limit()
                    if limit_result is not None:
                        return limit_result

                try:
                    if not session.get("__funix_id"):
                        session["__funix_id"] = uuid4().hex
                    if need_websocket:
                        function_kwargs = loads(ws.receive())
                    else:
                        function_kwargs = request.get_json()
                    kumo_callback()
                    if __pandas_use:
                        if function_id in dataframe_parse_metadata:
                            for need_argument in dataframe_parse_metadata[function_id]:
                                big_dict = {}
                                get_args = dataframe_parse_metadata[function_id][
                                    need_argument
                                ]
                                for get_arg in get_args:
                                    big_dict[get_arg] = deepcopy(
                                        function_kwargs[get_arg]
                                    )
                                    del function_kwargs[get_arg]
                                function_kwargs[
                                    need_argument
                                ] = __pandas_module.DataFrame(big_dict)
                    if function_id in parse_type_metadata:
                        for func_arg, func_arg_type_class in parse_type_metadata[
                            function_id
                        ].items():
                            if func_arg in function_kwargs:
                                try:
                                    function_kwargs[func_arg] = func_arg_type_class(
                                        function_kwargs[func_arg]
                                    )
                                except:
                                    # Oh, my `typing`
                                    continue

                    def original_result_to_pre_fill_metadata(
                        function_id_int: int,
                        function_call_result: Any,
                    ) -> None:
                        """
                        Document is on the way
                        """
                        function_call_address = str(function_id_int)
                        if pre_fill_metadata := get_pre_fill_metadata(
                            function_call_address
                        ):
                            for index_or_key in pre_fill_metadata:
                                if index_or_key is PreFillEmpty:
                                    set_global_variable(
                                        function_call_address + "_result",
                                        function_call_result,
                                    )
                                else:
                                    set_global_variable(
                                        function_call_address + f"_{index_or_key}",
                                        function_call_result[index_or_key],
                                    )

                    def pre_anal_result(function_call_result: Any):
                        """
                        Document is on the way
                        """
                        try:
                            original_result_to_pre_fill_metadata(
                                id(function), function_call_result
                            )
                            return anal_function_result(
                                function_call_result,
                                return_type_parsed,
                                cast_to_list_flag,
                            )
                        except:
                            return {
                                "error_type": "pre-anal",
                                "error_body": format_exc(),
                            }

                    @wraps(function)
                    def wrapped_function(**wrapped_function_kwargs):
                        """
                        The function's wrapper
                        """
                        # TODO: Best result handling, refactor it if possible
                        try:
                            function_call_result = function(**wrapped_function_kwargs)
                            return pre_anal_result(function_call_result)
                        except WrapperException as e:
                            return {
                                "error_type": "wrapper",
                                "error_body": str(e),
                            }
                        except:
                            return {
                                "error_type": "function",
                                "error_body": format_exc(),
                            }

                    @wraps(function)
                    def output_to_web_function(**wrapped_function_kwargs):
                        try:
                            fake_stdout = StdoutToWebsocket(ws)
                            org_stdout, sys.stdout = sys.stdout, fake_stdout
                            if isgeneratorfunction(function):
                                for single_result in function(
                                    **wrapped_function_kwargs
                                ):
                                    if single_result:
                                        print(single_result)
                            else:
                                function_result_ = function(**wrapped_function_kwargs)
                                if function_result_:
                                    print(function_result_)
                            sys.stdout = org_stdout
                        except:
                            ws.send(
                                dumps(
                                    {
                                        "error_type": "function",
                                        "error_body": format_exc(),
                                    }
                                )
                            )
                        ws.close()

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
                        empty_function_kwargs_error = {
                            "error_type": "wrapper",
                            "error_body": "No arguments passed to function.",
                        }
                        if need_websocket:
                            ws.send(dumps(empty_function_kwargs_error))
                            ws.close()
                        else:
                            return empty_function_kwargs_error
                    if secret_key:
                        if "__funix_secret" in function_kwargs:
                            if (
                                not __decorated_secret_functions_dict[function_id]
                                == function_kwargs["__funix_secret"]
                            ):
                                incorrect_secret_error = {
                                    "error_type": "wrapper",
                                    "error_body": "Provided secret is incorrect.",
                                }
                                if need_websocket:
                                    ws.send(dumps(incorrect_secret_error))
                                    ws.close()
                                else:
                                    return incorrect_secret_error
                            else:
                                del function_kwargs["__funix_secret"]
                        else:
                            no_secret_error = {
                                "error_type": "wrapper",
                                "error_body": "No secret provided.",
                            }
                            if need_websocket:
                                ws.send(dumps(no_secret_error))
                                ws.close()
                            else:
                                return no_secret_error

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
                            if need_websocket:
                                if print_to_web:
                                    ws.send(
                                        dumps(
                                            {
                                                "error_type": "wrapper",
                                                "error_body": "Funix cannot handle cell, print_to_web and stream mode "
                                                "in the same time",
                                            }
                                        )
                                    )
                                else:
                                    result = []
                                    for temp_function_result in function(**arg):
                                        function_result = pre_anal_result(
                                            temp_function_result
                                        )
                                        if isinstance(function_result, list):
                                            result.extend(function_result)
                                        else:
                                            result.append(function_result)
                                        ws.send(dumps({"result": result}))
                                        result = []
                                ws.close()
                            else:
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
                        if need_websocket:
                            if print_to_web:
                                output_to_web_function(**new_args)
                            else:
                                for temp_function_result in function(**new_args):
                                    function_result = pre_anal_result(
                                        temp_function_result
                                    )
                                    ws.send(dumps(function_result))
                                ws.close()
                        else:
                            return wrapped_function(**new_args)
                    else:
                        if need_websocket:
                            if print_to_web:
                                output_to_web_function(**function_kwargs)
                            else:
                                for temp_function_result in function(**function_kwargs):
                                    function_result = pre_anal_result(
                                        temp_function_result
                                    )
                                    ws.send(dumps(function_result))
                                ws.close()
                        else:
                            return wrapped_function(**function_kwargs)
                except:
                    error = {"error_type": "wrapper", "error_body": format_exc()}
                    if need_websocket:
                        ws.send(dumps(error))
                        ws.close()
                    else:
                        return error

            wrapper._decorator_name_ = "funix"

            if safe_module_now:
                wrapper.__setattr__("__name__", safe_module_now + "_" + function_name)

            if need_websocket:
                sock.route(f"/call/{function_id}")(wrapper)
            else:
                app.post(f"/call/{endpoint}")(wrapper)
                app.post(f"/call/{function_id}")(wrapper)
        return function

    return decorator


def funix_class(disable: bool = False):
    if disable:
        return lambda cls: cls
    return __funix_class


def __funix_class(cls):
    handled_object.append(id(cls))
    if inspect.isclass(cls):
        if not hasattr(cls, "__init__"):
            raise Exception("Class must have __init__ method!")

        f = RuntimeClassVisitor(cls.__name__, funix, cls)

        with open(inspect.getsourcefile(cls.__init__), "r") as file_:
            class_source_code = file_.read()

        f.visit(ast.parse(class_source_code))
        return cls
    else:
        for class_function in dir(cls):
            if not class_function.startswith("_"):
                function = getattr(cls, class_function)
                if callable(function):
                    org_id = id(getattr(type(cls), class_function))
                    if org_id not in class_method_ids_to_params:
                        funix()(function)
                    else:
                        params = class_method_ids_to_params[org_id]
                        args = params["args"]
                        kwargs = params["kwargs"]
                        funix(*args, **kwargs)(function)
