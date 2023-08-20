"""
This file is used to define the type hint of the Funix backend.
"""

from typing import Callable, Literal, NewType, Optional, TypeAlias, TypedDict, TypeVar

from funix.hint.layout import InputRow, OutputRow
from funix.widget import builtin

DestinationType = Optional[Literal["column", "row", "sheet"]]
"""
For yodas only, the destination of the page.
"""

Parameters = str | tuple
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

WidgetsValue = (
    list[AcceptableWidgets | tuple[AcceptableWidgets, dict]]
    | AcceptableWidgets
    | tuple[AcceptableWidgets, dict]
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

WhitelistValues = list[list] | list
"""
The value of the `whitelist`.

Types:
    list[list]: The whitelist, for example: [["a", "b"], ["c", "d"]].
    list: The whitelist, for example: ["a", "b"].
"""

WhitelistType = Optional[dict[Parameters, WhitelistValues]]
"""
The type of the `whitelist`.

Examples:
    {"a": ["a", "b"]} -> The parameter `a` has a whitelist, and the whitelist is `["a", "b"]`.
    {("a", "b"): [["a", "b"], ["c", "d"]]} -> The parameter `a` and `b` have a whitelist, and for `a` the whitelist is
                                              `["a", "b"]`, for `b` the whitelist is `["c", "d"]`.
"""

ExamplesValues = list[list] | list
"""
The value of the `examples`.

Types:
    list[list]: The examples, for example: [["a", "b"], ["c", "d"]].
    list: The examples, for example: ["a", "b"].
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

    when: dict[str, any]
    """
    The condition.

    `str` means the parameter name, `any` means the value. If the value of the parameter is equal to the value, elements
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
ArgumentWhitelistType = list[any]  # Same as the widget type
ArgumentExampleType = list[any]  # Same as the widget type
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

PreFillArgumentFrom = Callable | tuple[Callable, int]
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
Markdown: TypeAlias = _Markdown
"""
Markdown type.
For output.

Support Markdown like "**bold**" and "*italic*"
"""

_HTML = NewType("HTML", type(Optional[str]))
HTML: TypeAlias = _HTML
"""
HTML type.
For output.


Support HTML like "<span style='color: red'>red</span>"
"""

_Image = NewType("Images", type(BasicFileType))
Image: TypeAlias = _Image
"""
Image type.
For output.

See `BasicFileType` for more information.
"""

_Video = NewType("Videos", type(BasicFileType))
Video: TypeAlias = _Video
"""
Video type.
For output.

See `BasicFileType` for more information.
"""

_Audio = NewType("Audios", type(BasicFileType))
Audio: TypeAlias = _Audio
"""
Audio type.
For output.

See `BasicFileType` for more information.
"""

_File = NewType("Files", type(BasicFileType))
File: TypeAlias = _File
"""
File type.
For output.

See `BasicFileType` for more information.
"""

_Code = NewType("Code", type(Optional[str | CodeConfig]))
Code: TypeAlias = _Code
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


# ---- Built-in Output Widgets ----
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
# ---- Built-in Output Widgets ----


# ---- Decorator ----
class DecoratedFunctionListItem(TypedDict):
    """
    The item of the list `decorated_functions`.
    """

    name: str
    """
    The name (in frontend, title) of the function.
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


# ---- Decorator ----


def new_funix_type(widget: str, config_func: Optional[callable] = None) -> callable:
    """
    Decorator for creating new funix types.

    Parameters:
        widget (str): The widget to use for the new type.
        config_func (Optional[callable]): A function that returns a tuple of the form (type, config).

    Returns:
        callable: The decorator.
    """

    def decorator(cls) -> any:
        """
        Creates a new funix type.

        Parameters:
            cls (any): The class to decorate.

        Returns:
            any: The decorated class or getting the new funix type function.
        """
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
                    any: The decorated class.
                """
                cls.__funix__ = True
                cls.__funix_widget__ = widget
                cls.__funix_base__ = cls.__base__
                cls.__funix_config__ = config_func(*args, **kwargs)[1]
                return cls

            return new_cls_func

    return decorator
