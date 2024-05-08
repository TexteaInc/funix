"""
Funix decorator. The central logic of Funix.
"""
import ast
import inspect
from functools import wraps
from importlib import import_module
from inspect import getsource, isgeneratorfunction, signature
from secrets import token_hex
from types import ModuleType
from typing import Callable, Optional, Union
from uuid import uuid4

from funix.app import app, sock
from funix.config import banned_function_name_and_path
from funix.config.switch import GlobalSwitchOption
from funix.decorator.all_of import parse_all_of
from funix.decorator.annnotation_analyzer import register_ipywidgets, register_pandera
from funix.decorator.call import funix_call
from funix.decorator.file import enable_file_service
from funix.decorator.layout import handle_input_layout, handle_output_layout
from funix.decorator.limit import Limiter, parse_limiter_args
from funix.decorator.lists import (
    decorated_functions_list_append,
    enable_list,
    get_default_function_name,
    push_counter,
    set_default_function,
)
from funix.decorator.magic import parse_function_annotation
from funix.decorator.param import (
    create_parse_type_metadata,
    get_param_for_funix,
    parse_param,
)
from funix.decorator.pre_fill import parse_pre_fill
from funix.decorator.reactive import function_reactive_update, get_reactive_config
from funix.decorator.runtime import RuntimeClassVisitor
from funix.decorator.secret import (
    check_secret,
    get_app_secret,
    get_secret_by_id,
    set_function_secret,
)
from funix.decorator.theme import get_parsed_theme_fot_funix
from funix.decorator.widget import parse_argument_config, widget_parse
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
    PreFillType,
    ReactiveType,
    TreatAsType,
    WhitelistType,
    WidgetsType,
)
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

__wrapper_enabled: bool = False
"""
If the wrapper is enabled.
"""

now_module: str | None = None
"""
External passes to module, recorded here, are used to help funix decoration override config.
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


def funix(
    path: Optional[str] = None,
    title: Optional[str] = None,
    secret: bool | str = False,
    description: Optional[str] = "",
    session_description: Optional[str] = None,
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
    keep_last: bool = False,
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
        session_description(str): get description from session
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
        keep_last(bool): keep the last input and output in the frontend

    Returns:
        function: the decorated function

    Raises:
        Check code for details
    """

    def decorator(function: Callable) -> callable:
        """
        Decorator for functions to convert them to web apps

        Parameters:
            function(Callable): the function to be decorated

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

            create_parse_type_metadata(function_id)

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
            if app_secret := get_app_secret():
                set_function_secret(app_secret, function_id, function_title)
            elif secret:
                if isinstance(secret, bool):
                    set_function_secret(token_hex(16), function_id, function_title)
                else:
                    set_function_secret(secret, function_id, function_title)

            secret_key = get_secret_by_id(function_id) is not None

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
                    "keepLast": keep_last,
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

            safe_argument_config = {} if argument_config is None else argument_config

            parse_argument_config(safe_argument_config, decorated_params, function_name)

            parse_param_result = parse_param(
                function_params,
                json_schema_props,
                decorated_params,
                __pandas_use,
                __pandas_module,
                __pandera_module,
                function_id,
                function_name,
                parsed_theme,
            )

            if parse_param_result:
                return_type_parsed = parse_param_result

            safe_conditional_visible = (
                {} if conditional_visible is None else conditional_visible
            )
            all_of = parse_all_of(safe_conditional_visible, json_schema_props)

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
                return get_param_for_funix(
                    pre_fill, decorated_function, session_description
                )

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
                    return check_secret(function_id)

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
                result = funix_call(
                    limiters,
                    need_websocket,
                    __pandas_use,
                    __pandas_module,
                    function_id,
                    function,
                    return_type_parsed,
                    cast_to_list_flag,
                    json_schema_props,
                    print_to_web,
                    secret_key,
                    ws,
                )
                if result is not None:
                    return result

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
