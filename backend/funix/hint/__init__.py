"""
This file is used to define the type hint of the Funix backend.
"""

import os
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Literal,
    NewType,
    Optional,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
)

from funix.hint.layout import InputRow, OutputRow
from funix.widget import builtin

DestinationType = Optional[Literal["column", "row", "sheet"]]
"""
For yodas only, the destination of the page.
"""

Parameters = str | tuple[str, ...]
"""
Parameters.

Types:
    str: The name of the parameter.
    tuple: The name of the parameters, for example: `("a", "b", "c")`.
"""

AcceptableWidgets = Literal[
    "inputbox",
    "slider",
    "code",
    "textarea",
    "password",
    "switch",
    "checkbox",
    "sheet",
    "simple",
    "radio",
    "simple",
]
"""
Acceptable widgets. Implemented now.
"""

AcceptableWidgetsList = list(getattr(AcceptableWidgets, "__args__"))

WidgetsValue = (
    list[AcceptableWidgets | tuple[AcceptableWidgets, dict[str, Any]]]
    | AcceptableWidgets
    | tuple[AcceptableWidgets, dict[str, Any]]
)
"""
The value of the `widgets`.

Types:
    list[AcceptableWidgets]: The value of the widgets, for example: `["sheet", "inputbox"]`. Has a hierarchical
                             relationship.
    list[tuple[AcceptableWidgets, dict]]: The value of the widgets, for example:
                                          `[("slider", {"min": 1, "max": 200, "step": 2})]`.
    AcceptableWidgets: The value of the widgets, for example: `"sheet"`. Top-level use, as a rule, stands for all.
    tuple[AcceptableWidgets, dict]: The value of the widgets, for example:
                                    `("slider", {"min": 1, "max": 200, "step": 2})`.
"""

WidgetsType = Optional[dict[Parameters, WidgetsValue]]
"""
The type of the `widgets`.

Examples:
    {"a": "sheet"} -> The parameter `a` is a sheet.
    {"a": ["sheet", "inputbox"]} -> The parameter `a` is a sheet and the elements that inside the sheet are input boxes.
    {("a", "b"): "switch"} -> The parameter `a` and `b` are switches.
    {("a", "b"): ["sheet", "inputbox"]} -> The parameter `a` and `b` are sheets and the elements that inside the sheets
                                           are input boxes.
"""

TreatAsValues = Literal["column", "config", "cell"]
"""
Acceptable values of `treat_as` attribute.

Default: "config", for list or typing.List, please choose "column" or "cell".
"""

TreatAsType = Optional[dict[Parameters, TreatAsValues]]
"""
The type of the `treat_as` attribute.

Examples:
    {"a": "column"} -> The parameter `a` is a column.
    {("a", "b"): "cell"} -> The parameter `a` and `b` are cells.
"""

WhitelistValues = list[list[str]] | list[str] | Callable[..., Any]
"""
The value of the `whitelist`.

Types:
    list[list]: The whitelist, for example: [["a", "b"], ["c", "d"]].
    list: The whitelist, for example: ["a", "b"].
    function: return a list of values.
"""

WhitelistType = Optional[dict[Parameters, WhitelistValues]]
"""
The type of the `whitelist`.

Examples:
    {"a": ["a", "b"]} -> The parameter `a` has a whitelist, and the whitelist is `["a", "b"]`.
    {("a", "b"): [["a", "b"], ["c", "d"]]} -> The parameter `a` and `b` have a whitelist, and for `a` the whitelist is
                                              `["a", "b"]`, for `b` the whitelist is `["c", "d"]`.
"""

DynamicDefaultsType = Optional[dict[Parameters, Callable[..., Any]]]
"""
The type of the `dynamic_defaults`.

Examples:
    {"a": b} -> The parameter `a` has a dynamic default value, and the default value is the result of the function `b`.
"""

ExamplesValues = list[list[str]] | list[str] | Callable[..., Any]
"""
The value of the `examples`.

Types:
    list[list]: The examples, for example: [["a", "b"], ["c", "d"]].
    list: The examples, for example: ["a", "b"].
    function: return a list of values.
"""

ExamplesType = Optional[dict[Parameters, ExamplesValues]]
"""
The type of the `examples`.

Examples:
    {"a": ["a", "b"]} -> The parameter `a` has examples, and the examples are `"a"` and `"b"`.
    {("a", "b"): [["a", "b"], ["c", "d"]]} -> The parameter `a` and `b` have examples, and for `a` the examples are
                                              `"a"`, `"b"`, for `b` the examples are `"c"`, `"d"`.
"""

LabelsType = Optional[dict[Parameters, str]]
"""
The type of the `argument_labels`.

Examples:
    {"a": "A"} -> The parameter `a` has a label, and the label is `A`.
    {("a", "b"): "A"} -> The parameter `a` and `b` have the same label, and the label is `A`.
"""

InputLayout = Optional[list[InputRow]]
"""
The type of the `input_layout`.

See `InputRow` for more information.
"""

OutputLayout = Optional[list[OutputRow]]
"""
The type of the `output_layout`.

See `OutputRow` for more information.
"""

DirectionType = Optional[Literal["row", "column", "row-reverse", "column-reverse"]]
"""
The type of the `direction`.

Default: "row".
"""


class ConditionalVisible(TypedDict):
    """
    Conditional visible.
    """

    when: dict[str, Any]
    """
    The condition.

    `str` means the parameter name, `Any` means the value. If the value of the parameter is equal to the value, elements
    that in `then` will be visible.
    """

    show: list[str]
    """
    The parameters that will be visible if the condition is true.
    """


ConditionalVisibleType = Optional[list[ConditionalVisible]]
"""
The type of the `conditional_visible`.

Examples:
    [{"when": {"a": "b"}, "show": ["c"]}] -> If the value of the parameter `a` is equal to `"b"`, the parameter `c`
                                             will be visible.
"""

ArgumentConfigKeys = Literal["treat_as", "whitelist", "example", "widget", "label"]
"""
The keys of `argument_config[widget]`.
"""

ArgumentTreatAsType = str
ArgumentWhitelistType = list[Any]  # Same as the widget type
ArgumentExampleType = list[Any]  # Same as the widget type
ArgumentWidgetType = str
ArgumentLabelType = str

ArgumentConfigType = Optional[
    dict[
        Parameters,
        dict[
            ArgumentConfigKeys,
            ArgumentTreatAsType
            | ArgumentWhitelistType
            | ArgumentExampleType
            | ArgumentWidgetType
            | ArgumentLabelType,
        ],
    ]
]
"""
The type of the `argument_config`.

Examples:
    {"a": {"widget": "sheet"}} -> The parameter `a` has a widget, and the widget is `sheet`.
"""

PreFillArgumentFrom = Callable[..., Any] | tuple[Callable[..., Any], int]
"""
Pre-fill argument from.

Types:
    callable: The function.
    tuple[callable, int]: The function and the index.
"""

PreFillType = Optional[dict[str, PreFillArgumentFrom]]
"""
The type of the `pre_fill`.

Examples:
    {"a": "b"} -> The parameter `a` will be pre-filled from the function `b`'s result.
    {"a": ("b", 1)} -> The parameter `a` will be pre-filled from the function `b`'s result, and the index is `1`.
"""

PreFillEmpty = TypeVar("PreFillEmpty")

ReactiveType = Optional[
    dict[str, Callable[..., Any] | tuple[Callable[..., Any], dict[str, str]]]
]
"""
Document is on the way
"""

ComponentMuiComponents = [
    "@mui/material/TextField",
    "@mui/material/Switch",
    "@mui/material/Checkbox",
    "@mui/material/Slider",
    "@mui/material/Rating",
]

ComponentTypes = Union[str, bool, int, float]

ComponentMaps: dict[Any, list[str]] = {
    str: ["@mui/material/TextField"],
    bool: ["@mui/material/Switch", "@mui/material/Checkbox"],
    int: ["@mui/material/Slider", "@mui/material/TextField", "@mui/material/Rating"],
    float: ["@mui/material/Slider", "@mui/material/TextField", "@mui/material/Rating"],
}
"""
The component maps.
"""


class CodeConfig(TypedDict):
    """
    The config of the code box.

    For output.
    """

    lang: Optional[str]
    """
    The language of the code.
    """

    code: Optional[str]
    """
    The code.
    """


BasicFileType = Optional[str | bytes]
"""
Support URL, path, bytes

For example: "https://example.org/imgs/1.png"
"""

_Markdown = NewType("Markdown", type(Optional[str]))
Markdown: TypeAlias = _Markdown  # type: ignore
"""
Markdown type.
For output.

Support Markdown like "**bold**" and "*italic*"
"""

_HTML = NewType("HTML", type(Optional[str]))
HTML: TypeAlias = _HTML  # type: ignore
"""
HTML type.
For output.


Support HTML like "<span style='color: red'>red</span>"
"""

_Image = NewType("Images", type(BasicFileType))
Image: TypeAlias = _Image  # type: ignore
"""
Image type.
For output.

See `BasicFileType` for more information.
"""

_Video = NewType("Videos", type(BasicFileType))
Video: TypeAlias = _Video  # type: ignore
"""
Video type.
For output.

See `BasicFileType` for more information.
"""

_Audio = NewType("Audios", type(BasicFileType))
Audio: TypeAlias = _Audio  # type: ignore
"""
Audio type.
For output.

See `BasicFileType` for more information.
"""

_File = NewType("Files", type(BasicFileType))
File: TypeAlias = _File  # type: ignore
"""
File type.
For output.

See `BasicFileType` for more information.
"""

_Code = NewType("Code", type(Optional[str | CodeConfig]))
Code: TypeAlias = _Code  # type: ignore
"""
Code type.
For output.


Support Code like:

{
    "lang": "python",
    "code": "print('hello world')"
}

or just a string like "print('hello world')"
"""

# ---- Built-in Input Widgets ----
IntInputBox: TypeAlias = builtin.IntInputBox
IntSlider = builtin.IntSlider
FloatInputBox: TypeAlias = builtin.FloatInputBox
FloatSlider = builtin.FloatSlider
StrCode = builtin.StrCode
StrInputBox: TypeAlias = builtin.StrInputBox
StrTextarea: TypeAlias = builtin.StrTextarea
StrPassword: TypeAlias = builtin.StrPassword
BoolCheckBox: TypeAlias = builtin.BoolCheckBox
BoolSwitch: TypeAlias = builtin.BoolSwitch
BytesImage: TypeAlias = builtin.BytesImage
BytesVideo: TypeAlias = builtin.BytesVideo
BytesAudio: TypeAlias = builtin.BytesAudio
BytesFile: TypeAlias = builtin.BytesFile


# ---- Built-in Input Widgets ----


# ---- Decorator ----
class DecoratedFunctionListItem(TypedDict):
    """
    The item of the list `decorated_functions`.
    """

    name: str
    """
    The name (in frontend, title) of the function.
    """

    id: str
    """
    The id of the function.
    """

    path: str
    """
    The path of the function.
    """

    module: Optional[str]
    """
    The module of the function.
    """

    secret: Optional[str]
    """
    The secret of the function.
    """

    websocket: bool
    """
    Is this function is run in a websocket?
    """


# ---- Decorator ----


custom_cls_ids: list[int] = []


def new_funix_type_with_config_func(
    widget: str, config_func: Optional[callable] = None
) -> callable:
    """
    Decorator for creating new funix types.

    Parameters:
        widget (str): The widget to use for the new type.
        config_func (Optional[callable]): A function that returns a tuple of the form (type, config).

    Returns:
        callable: The decorator.
    """

    def decorator(cls) -> Any:
        """
        Creates a new funix type.

        Parameters:
            cls (Any): The class to decorate.

        Returns:
            Any: The decorated class or getting the new funix type function.
        """
        custom_cls_ids.append(id(cls))
        if config_func is None:
            cls.__funix__ = True
            cls.__funix_widget__ = widget
            cls.__funix_base__ = cls.__base__
            return cls
        else:

            def new_cls_func(*args, **kwargs):
                """
                Creates a new funix type with a config function.

                Parameters:
                    *args: The arguments to pass to the config function.
                    **kwargs: The keyword arguments to pass to the config function.

                Returns:
                    Any: The decorated class.
                """
                cls.__funix__ = True
                cls.__funix_widget__ = widget
                cls.__funix_base__ = cls.__base__
                cls.__funix_config__ = config_func(*args, **kwargs)[1]
                return cls

            return new_cls_func

    return decorator


class NewFunixWidgetType(TypedDict):
    """
    New Funix widget type.

    For new funix typing.
    """

    name: Optional[str]
    """
    The name of the widget.
    """

    config: Optional[dict]
    """
    The config of the widget.
    """


class NewFunixWithComponentType(TypedDict):
    """
    New Funix widget type.

    For new funix typing. With component.
    """

    props: Optional[dict]
    """
    The props of the widget.
    """

    widget: Optional[str]
    """
    The component name of the widget.
    """


def new_funix_type(
    widget: Union[NewFunixWidgetType, NewFunixWithComponentType, dict],
) -> callable:
    """
    Decorator for creating new funix types.

    Parameters:
        widget (NewFunixWidgetType): The widget to use for the new type.

    Returns:
        callable: The decorator.
    """

    def decorator(cls) -> Any:
        custom_cls_ids.append(id(cls))
        cls.__funix__ = True
        if not widget.get("name") and not widget.get("widget"):
            raise ValueError("You must specify a name or a widget")
        cls.__funix_base__ = cls.__base__
        if widget.get("name", None):
            cls.__funix_widget__ = widget["name"]
            if "config" in widget and widget["config"] is not None:
                cls.__funix_config__ = widget["config"]
        elif widget.get("widget", None):
            if "props" in widget and widget["props"] is not None:
                cls.__funix_props__ = widget["props"]
            if "widget" in widget and widget["widget"] is not None:
                if widget["widget"] not in ComponentMuiComponents:
                    raise ValueError(
                        f"The widget {widget['widget']} is not a valid component."
                    )
                if cls.__base__ not in ComponentMaps:
                    raise ValueError(
                        f"The {cls.__base__} is not a valid type for a widget."
                    )
                if widget["widget"] not in ComponentMaps[cls.__base__]:
                    raise ValueError(
                        f"The widget {widget['widget']} is not match the type {cls.__base__}."
                    )
                cls.__funix_component__ = widget["widget"]
        return cls

    return decorator


class WrapperException(Exception):
    """
    A wrapper exception for internal error handling, will be converted to
    {"error_type": "wrapper", "error_body": str(exception)} and send to frontend
    """

    pass


class LogLevel(Enum):
    """
    The log level.
    """

    OFF = 0
    """
    Turn off the log.
    """

    OPTIONAL = 1
    """
    User can choose to turn off the log.
    """

    MANDATORY = 2
    """
    If use want to use the service, the log is mandatory.
    """

    @staticmethod
    def get_level() -> "LogLevel":
        """
        Get the log level from the environment variable.

        Returns:
            LogLevel: The log level.
        """
        funix_telemetry = os.environ.get("FUNIX_TELEMETRY", "off").lower()

        if funix_telemetry == "optional":
            return LogLevel.OPTIONAL
        elif funix_telemetry == "mandatory":
            return LogLevel.MANDATORY
        elif funix_telemetry == "off":
            return LogLevel.OFF
        else:
            return LogLevel.OFF


class LimitSource(Enum):
    """
    rate limit based on what value
    """

    # Based on browser session
    SESSION = auto()

    # Based on IP
    IP = auto()
