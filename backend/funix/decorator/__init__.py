"""
Funix decorator. The central logic of Funix.
"""
import ast
import dataclasses
import inspect
import pathlib
import re
import sys
import time
from collections import deque
from copy import deepcopy
from enum import Enum, auto
from functools import wraps
from importlib import import_module
from inspect import Parameter, Signature, getsource, isgeneratorfunction, signature
from io import StringIO
from json import dumps, loads
from secrets import token_hex
from traceback import format_exc
from types import ModuleType
from typing import Any, Callable, Optional
from urllib.request import urlopen
from uuid import uuid4

from flask import Response, request, session
from requests import post
from requests.structures import CaseInsensitiveDict

from funix.app import app, sock
from funix.config import (
    banned_function_name_and_path,
    supported_basic_file_types,
    supported_basic_types,
    supported_basic_types_dict,
    supported_upload_widgets,
)
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
from funix.decorator.magic import (
    anal_function_result,
    convert_row_item,
    function_param_to_widget,
    get_type_dict,
    get_type_widget_prop,
)
from funix.decorator.runtime import RuntimeClassVisitor
from funix.hint import (
    ArgumentConfigType,
    ConditionalVisibleType,
    DecoratedFunctionListItem,
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
from funix.theme import get_dict_theme, parse_theme
from funix.util.module import funix_menu_to_safe_function_name
from funix.util.text import un_indent
from funix.util.uri import is_valid_uri
from funix.widget import generate_frontend_widget_config

__ipython_type_convert_dict = {
    "IPython.core.display.Markdown": "Markdown",
    "IPython.lib.display.Markdown": "Markdown",
    "IPython.core.display.HTML": "HTML",
    "IPython.lib.display.HTML": "HTML",
    "IPython.core.display.Image": "Images",
    "IPython.lib.display.Image": "Images",
    "IPython.core.display.Audio": "Audios",
    "IPython.lib.display.Audio": "Audios",
    "IPython.core.display.Video": "Videos",
    "IPython.lib.display.Video": "Videos",
}
"""
A dict, key is the IPython type name, value is the Funix type name.
"""

__dataframe_convert_dict = {
    "pandera.typing.pandas.DataFrame": "Dataframe",
    "pandas.core.frame.DataFrame": "Dataframe",
}
"""
A dict, key is the dataframe type name, value is the Funix type name.
"""

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

pre_fill_metadata: dict[str, list[str | int | PreFillEmpty]] = {}
"""
A dict, key is function ID, value is a list of indexes/keys of pre-fill parameters.
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

module_functions_counter: dict[str, int] = {}
"""
A dict, key is module name, value is the number of functions in the module.
"""

default_function: str | None = None
"""
Default function id.
"""

cached_list_functions: list[dict] = []
"""
Cached list functions. For `/list` route.
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

default_function_name: str | None = None
"""
Default function name.
"""

ip_headers: list[str] = []
"""
IP headers for extraction, useful for applications behind reverse proxies

e.g. `X-Forwarded-For`, `X-Real-Ip` e.t.c
"""

decorated_function_ids: list[int] = []
"""
Decorated function ids.
"""

class_method_ids_to_params: dict[int, dict] = {}
"""
Class method ids to params.
"""


class StdoutToWebsocket:
    def __init__(self, ws):
        self.ws = ws
        self.value = StringIO()

    def write(self, data):
        self.value.write(data)
        self.ws.send(dumps([self.value.getvalue()]))

    def writelines(self, data):
        self.value.writelines(data)
        self.ws.send(dumps([self.value.getvalue()]))

    def flush(self):
        self.value.flush()
        self.ws.send(dumps([self.value.getvalue()]))
        self.value = StringIO()


def funix_method(*args, **kwargs):
    def decorator(func):
        if "disable" in kwargs and kwargs["disable"]:
            class_method_ids_to_params[id(func)] = {
                "disable": kwargs["disable"],
            }
        else:
            class_method_ids_to_params[id(func)] = {
                "args": args,
                "kwargs": kwargs,
            }
        return func

    return decorator


class LimitSource(Enum):
    """
    rate limit based on what value
    """

    # Based on browser session
    SESSION = auto()

    # Based on IP
    IP = auto()


@dataclasses.dataclass
class Limiter:
    call_history: dict
    # How many calls client can send between each interval set by `period`
    max_calls: int
    # Max call interval time, in seconds
    period: int
    source: LimitSource

    def __init__(
        self,
        max_calls: int = 10,
        period: int = 60,
        source: LimitSource = LimitSource.SESSION,
    ):
        if type(max_calls) is not int:
            raise TypeError("type of `max_calls` is not int")
        if type(period) is not int:
            raise TypeError("type of `period` is not int")
        if type(source) is not LimitSource:
            raise TypeError("type of `source` is not LimitSource")

        self.source = source
        self.max_calls = max_calls
        self.period = period
        self.call_history = {}

    @staticmethod
    def ip(max_calls: int, period: int = 60):
        return Limiter(max_calls=max_calls, period=period, source=LimitSource.IP)

    @staticmethod
    def session(max_calls: int, period: int = 60):
        return Limiter(max_calls=max_calls, period=period, source=LimitSource.SESSION)

    @staticmethod
    def _dict_get_int(
        dictionary: dict | CaseInsensitiveDict, key: str
    ) -> Optional[int]:
        if key not in dictionary:
            return None
        value = dictionary[key]
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        raise ValueError(
            f"The value of key `{key}` is `{value}`, cannot parse to integer"
        )

    @staticmethod
    def from_dict(dictionary: dict):
        converted = CaseInsensitiveDict(dictionary)
        ip = Limiter._dict_get_int(converted, "per_ip")
        session = Limiter._dict_get_int(converted, "per_browser")

        if ip is not None and session is not None:
            raise TypeError(
                "`per_ip` and `per_browser` are conflicting options in a single dict"
            )

        if ip is None and session is None:
            raise TypeError("`per_ip` or `per_browser` is required")

        max_calls = ip or session
        if ip is not None:
            source = LimitSource.IP
        if session is not None:
            source = LimitSource.SESSION
        period = Limiter._dict_get_int(converted, "period") or 60

        return Limiter(max_calls=max_calls, period=period, source=source)

    def rate_limit(self) -> Optional[Response]:
        call_history = self.call_history
        match self.source:
            case LimitSource.IP:
                source: Optional[str] = None
                for header in ip_headers:
                    if header in request.headers:
                        source = request.headers[header]
                        break

                if source is None:
                    source = request.remote_addr

            case LimitSource.SESSION:
                source = session.get("__funix_id")

        if source not in call_history:
            call_history[source] = deque()

        queue = call_history[source]
        current_time = time.time()

        while len(queue) > 0 and current_time - queue[0] > self.period:
            queue.popleft()

        if len(queue) >= self.max_calls:
            time_passed = current_time - queue[0]
            time_to_wait = int(self.period - time_passed)
            error_message = {
                "error_body": f"Rate limit exceeded. Please try again in {time_to_wait} seconds.",
                "error_type": "safe_checker",
            }
            return Response(
                dumps(error_message), status=429, mimetype="application/json"
            )

        queue.append(current_time)
        return None


def set_ip_header(headers: Optional[list[str]]):
    global ip_headers
    if headers is None:
        return

    if len(headers) == 0:
        return

    ip_headers = headers


def parse_limiter_args(rate_limit: Limiter | list | dict, arg_name: str = "rate_limit"):
    limiters: Optional[list[Limiter]] = []

    if isinstance(rate_limit, Limiter):
        limiters = []
        limiters.append(rate_limit)
    elif isinstance(rate_limit, dict):
        converted = CaseInsensitiveDict(rate_limit)

        per_ip = Limiter._dict_get_int(converted, "per_ip")
        per_session = Limiter._dict_get_int(converted, "per_browser")
        limiters = []
        if per_ip:
            limiters.append(Limiter.ip(per_ip))
        if per_session:
            limiters.append(Limiter.ip(per_session))
        if len(limiters) == 0:
            raise TypeError(
                f"Dict passed for `{arg_name}` but no limiters are provided, something wrong."
            )

    elif isinstance(rate_limit, list):
        limiters = []
        for element in rate_limit:
            if isinstance(element, Limiter):
                limiters.append(element)
            elif isinstance(element, dict):
                limiters.append(Limiter.from_dict(element))
            else:
                raise TypeError(f"Invalid arguments, unsupported type for `{arg_name}`")

    else:
        raise TypeError(f"Invalid arguments, unsupported type for `{arg_name}`")

    return limiters


global_rate_limiters: list[Limiter] = []


def is_empty_function_list() -> bool:
    """
    Check if the function list is empty.

    Returns:
        bool: True if empty, False otherwise.
    """
    return len(__decorated_functions_list) == 0


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


def set_rate_limiters(limiters: list[Limiter]):
    global global_rate_limiters
    global_rate_limiters = limiters


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


def set_default_function_name(name: str) -> None:
    """
    Set this function as default.
    """
    global default_function_name
    default_function_name = name


def make_decorated_functions_happy() -> list[dict]:
    """
    Make the decorated functions happy,
    """
    global cached_list_functions, __decorated_functions_list
    if cached_list_functions:
        return cached_list_functions
    new_decorated_functions_list = []
    for i in __decorated_functions_list:
        if i["module"] in module_functions_counter:
            if module_functions_counter[i["module"]] == 1:
                if "." in i["module"]:
                    i["module"] = ".".join(i["module"].split(".")[0:-1])
                else:
                    i["module"] = None
        new_decorated_functions_list.append(i)
    cached_list_functions = new_decorated_functions_list
    return new_decorated_functions_list


def enable_wrapper() -> None:
    """
    Enable the wrapper, this will add the list and file path to the app.
    """
    global __wrapper_enabled, default_function
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
                "list": make_decorated_functions_happy(),
                "default_function": default_function,
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


def import_theme(
    source: str | dict,
    alias: Optional[str],
) -> None:
    """
    Import a theme from path, url or dict.

    Parameters:
        source (str | dict): The path, url or dict of the theme.
        alias (str): The theme alias.

    Raises:
        ValueError: If the theme already exists.

    Notes:
        Check the `funix.theme.get_dict_theme` function for more information.
    """
    global __themes
    if isinstance(source, str):
        if is_valid_uri(source):
            theme = get_dict_theme(None, source)
        else:
            theme = get_dict_theme(source, None)
    else:
        theme = source
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
    rate_limit: Limiter | list | dict = [],
    reactive: ReactiveType = None,
    print_to_web: bool = False,
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

    Returns:
        function: the decorated function

    Raises:
        Check code for details
    """
    global __parsed_themes, pre_fill_metadata, parse_type_metadata

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
        global default_function
        if __wrapper_enabled:
            if menu:
                module_functions_counter[menu] = (
                    module_functions_counter.get(menu, 0) + 1
                )
            elif now_module:
                module_functions_counter[now_module] = (
                    module_functions_counter.get(now_module, 0) + 1
                )
            else:
                module_functions_counter["$Funix_Main"] = (
                    module_functions_counter.get("$Funix_Main", 0) + 1
                )

            function_id = str(uuid4())

            if default:
                default_function = function_id

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
                    default_function = function_id
            elif default_function_name:
                if function_name == default_function_name:
                    default_function = function_id

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

            function_title = title if title is not None else function_name

            function_description = description
            if function_description == "" or function_description is None:
                function_docstring = getattr(function, "__doc__")
                if function_docstring:
                    function_description = un_indent(function_docstring)

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
                if unique_function_name:
                    endpoint = unique_function_name
                else:
                    endpoint = function_name
            else:
                if path in banned_function_name_and_path:
                    raise Exception(f"{function_name}'s path: {path} is not allowed")
                endpoint = path.strip("/")

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

            decorated_function_ids.append(id(function))

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
                for reactive_param in reactive.keys():
                    if reactive_param not in function_params:
                        raise ValueError(
                            f"Reactive param `{reactive_param}` not found in function `{function_name}`"
                        )
                    callable_or_with_config = reactive[reactive_param]

                    if isinstance(callable_or_with_config, tuple):
                        callable_ = callable_or_with_config[0]
                        full_config = callable_or_with_config[1]
                    else:
                        callable_ = callable_or_with_config
                        full_config = None

                    callable_params = signature(callable_).parameters

                    for callable_param in dict(callable_params.items()).values():
                        if (
                            callable_param.kind == Parameter.VAR_KEYWORD
                            or callable_param.kind == Parameter.VAR_POSITIONAL
                        ):
                            reactive_config[reactive_param] = (callable_, {})
                            break

                    if reactive_param not in reactive_config:
                        if full_config:
                            reactive_config[reactive_param] = (callable_, full_config)
                        else:
                            reactive_config[reactive_param] = (callable_, {})
                            for key in dict(callable_params.items()).keys():
                                if key not in function_params:
                                    raise ValueError(
                                        f"The key {key} is not in function, please write full config"
                                    )
                                reactive_config[reactive_param][1][key] = key

                def function_reactive_update():
                    reactive_param_value = {}

                    form_data = request.get_json()

                    for key_, item_ in reactive_config.items():
                        argument_key: str = key_
                        callable_function: Callable = item_[0]
                        callable_config: dict[str, str] = item_[1]

                        try:
                            if callable_config == {}:
                                reactive_param_value[argument_key] = callable_function(
                                    **form_data
                                )
                            else:
                                new_form_data = {}
                                for key__, value in callable_config.items():
                                    new_form_data[key__] = form_data[value]
                                reactive_param_value[argument_key] = callable_function(
                                    **new_form_data
                                )
                        except:
                            pass

                    if reactive_param_value == {}:
                        return {"result": None}

                    return {"result": reactive_param_value}

                function_reactive_update.__name__ = function_name + "_reactive_update"

                if safe_module_now:
                    function_reactive_update.__name__ = (
                        f"{safe_module_now}_{function_reactive_update.__name__}"
                    )

                app.post(f"/update/{function_id}")(function_reactive_update)
                app.post(f"/update/{endpoint}")(function_reactive_update)

            __decorated_functions_list.append(
                {
                    "name": function_title,
                    "path": endpoint,
                    "module": replace_module,
                    "secret": secret_key,
                    "id": function_id,
                    "websocket": need_websocket,
                    "reactive": has_reactive_params,
                }
            )

            if show_source:
                source_code = getsource(function)
            else:
                source_code = ""

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
                            full_type_name = (
                                getattr(return_annotation_type, "__module__")
                                + "."
                                + return_annotation_type_name
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
                            if full_type_name in __ipython_type_convert_dict:
                                return_annotation_type_name = (
                                    __ipython_type_convert_dict[full_type_name]
                                )
                            elif full_type_name in __dataframe_convert_dict:
                                return_annotation_type_name = __dataframe_convert_dict[
                                    full_type_name
                                ]
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
                                    if hasattr(
                                        function_signature.return_annotation,
                                        "__module__",
                                    ):
                                        full_name = (
                                            getattr(
                                                function_signature.return_annotation,
                                                "__module__",
                                            )
                                            + "."
                                            + getattr(
                                                function_signature.return_annotation,
                                                "__name__",
                                            )
                                        )
                                        if full_name in __ipython_type_convert_dict:
                                            return_type_parsed = (
                                                __ipython_type_convert_dict[full_name]
                                            )
                                        elif full_name in __dataframe_convert_dict:
                                            return_type_parsed = (
                                                __dataframe_convert_dict[full_name]
                                            )
                                        else:
                                            # TODO: DO MORE
                                            return_type_parsed = None
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
                    elif "divider" in row_item:
                        row_item_done["type"] = "divider"
                        if isinstance(row_item["divider"], str):
                            row_item_done["content"] = row_item_done["divider"]
                        row_item_done.pop("divider")
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
                    if "divider" in row_item:
                        row_item_done["type"] = "divider"
                        if isinstance(row_item["divider"], str):
                            row_item_done["content"] = row_item_done["divider"]
                        row_item_done.pop("divider")
                    elif "code" in row_item:
                        row_item_done = row_item
                        row_item_done["type"] = "code"
                        row_item_done["content"] = row_item_done["code"]
                        row_item_done.pop("code")
                    elif "return_index" in row_item:
                        row_item_done["type"] = "return_index"
                        row_item_done["index"] = row_item_done["return_index"]
                        row_item_done.pop("return_index")
                        if isinstance(row_item_done["index"], int):
                            return_output_indexes.append(row_item_done["index"])
                        elif isinstance(row_item_done["index"], list):
                            return_output_indexes.extend(row_item_done["index"])
                    row_layout.append(row_item_done)
                return_output_layout.append(row_layout)

            if pre_fill:
                for _, from_arg_function_info in pre_fill.items():
                    if isinstance(from_arg_function_info, tuple):
                        from_arg_function_address = str(id(from_arg_function_info[0]))
                        from_arg_function_index_or_key = from_arg_function_info[1]
                        if from_arg_function_address in pre_fill_metadata:
                            pre_fill_metadata[from_arg_function_address].append(
                                from_arg_function_index_or_key
                            )
                        else:
                            pre_fill_metadata[from_arg_function_address] = [
                                from_arg_function_index_or_key
                            ]
                    else:
                        from_arg_function_address = str(id(from_arg_function_info))
                        if from_arg_function_address in pre_fill_metadata:
                            pre_fill_metadata[from_arg_function_address].append(
                                PreFillEmpty
                            )
                        else:
                            pre_fill_metadata[from_arg_function_address] = [
                                PreFillEmpty
                            ]

            def create_decorated_params(arg_name: str) -> None:
                """
                Creates a decorated_params entry for the given arg_name if it doesn't exist

                Parameters:
                    arg_name (str): The name of the argument
                """
                if arg_name not in decorated_params:
                    decorated_params[arg_name] = {}

            def put_props_in_params(
                arg_name: str, prop_name: str, prop_value: Any
            ) -> None:
                """
                Puts the given prop_name and prop_value in the decorated_params entry for the given arg_name

                Parameters:
                    arg_name (str): The name of the argument
                    prop_name (str): The name of the prop
                    prop_value (Any): The value of the prop
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

            def iter_over_prop(
                argument_type: str,
                argument: dict[str | tuple, Any] | None,
                callback,
            ):
                """
                callback: pass in (argument_type, key, key_idx, value)
                """
                if argument is None:
                    return

                for arg_idx, arg_key in enumerate(argument):
                    if isinstance(arg_key, str):
                        callback(argument_type, arg_key, 0, argument[arg_key])
                    elif isinstance(arg_key, tuple):
                        for key_idx, single_key in enumerate(arg_key):
                            callback(
                                argument_type, single_key, key_idx, argument[arg_key]
                            )
                    else:
                        raise TypeError(
                            f"Argument `{argument_type}` has invalid key type {type(argument)}"
                        )

            function_params_name: list[str] = list(function_params.keys())

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

            def process_widgets(arg_type: str, arg_key: str, key_idx: int, value: any):
                parsed_widget = parse_widget(value)
                for expanded_key in expand_wildcards(arg_key, function_params_name):
                    put_props_in_params(expanded_key, arg_type, parsed_widget)

            iter_over_prop("widget", widgets, process_widgets)

            def process_title(arg_type: str, arg_key: str, key_idx: int, value: any):
                for expanded_key in expand_wildcards(arg_key, function_params_name):
                    put_props_in_params(expanded_key, arg_type, value)

            iter_over_prop("title", argument_labels, process_title)

            def process_treat_as(arg_type: str, arg_key: str, key_idx: int, value: any):
                put_props_in_params(arg_key, arg_type, value)

            iter_over_prop("treat_as", treat_as, process_treat_as)

            def process_examples_and_whitelist(
                arg_type: str, arg_key: str, key_idx: int, value: any
            ):
                put_props_in_params(arg_key, arg_type, value[key_idx])
                check_example_whitelist(arg_key)

            iter_over_prop("example", examples, process_examples_and_whitelist)
            iter_over_prop("whitelist", whitelist, process_examples_and_whitelist)

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
                        if function_call_address in pre_fill_metadata:
                            for index_or_key in pre_fill_metadata[
                                function_call_address
                            ]:
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


def funix_class():
    return __funix_class


def __funix_class(cls):
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
                        if "disable" in params:
                            continue
                        args = params["args"]
                        kwargs = params["kwargs"]
                        funix(*args, **kwargs)(function)
