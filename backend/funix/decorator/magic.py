"""
Magic functions, refactor it if you can.

I can't guarantee that the type annotations and comments here are correct, because the logic and naming here is so
complex and confusing that I copied them from `decorator/__init__.py`.

The main features of the functions here are to analyze the types/annotations/parameters and return the processed data
to the frontend for direct use or as middleware to return the pre-processed data awaiting further analysis.

However, their logic is complex, with a lot of if-else, no comments and no unit tests, so it is not very good to infer
the types of parameters, the types of return values and the rough logic.
"""
import ast
import io
import json
from importlib import import_module
from inspect import Parameter, Signature, getsource, signature
from re import Match, search
from types import ModuleType
from typing import Any, Callable

from funix.config import (
    builtin_widgets,
    dataframe_convert_dict,
    ipython_type_convert_dict,
    supported_basic_file_types,
    supported_basic_types,
    supported_basic_types_dict,
)
from funix.decorator.annnotation_analyzer import analyze
from funix.decorator.file import get_static_uri, handle_ipython_audio_image_video
from funix.decorator.lists import (
    get_function_detail_by_uuid,
    get_function_uuid_with_id,
    get_class_method_funix,
)

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


__ipython_use = False
"""
Whether Funix can handle IPython-related logic
"""

__ipython_display: None | ModuleType = None

try:
    __ipython_display = import_module("IPython.display")

    __ipython_use = True
except:
    pass


mpld3: ModuleType | None = None
"""
The mpld3 module.
"""


def get_type_dict(annotation: any) -> dict:
    """
    Get the type dict of the annotation.

    Parameters:
        annotation (any): The annotation for analysis.

    Examples:
        >>> import typing
        >>> from funix.decorator.magic import get_type_dict
        >>>
        >>> assert get_type_dict(int) == {"type": "int"}
        >>> assert get_type_dict(type(True)) == {"type": "bool"}
        >>> assert get_type_dict(typing.Literal["a", "b", "c"]) == {'type': 'str', 'whitelist': ('a', 'b', 'c')}
        >>> assert get_type_dict(typing.Optional[int]) == {'optional': True, 'type': 'int'}

    Returns:
        dict: The type dict.
    """
    # TODO: String magic, refactor it if you can
    anal_result = analyze(annotation)
    if anal_result:
        return anal_result
    if annotation is None:
        # Special case for None, let frontend handle `null`
        return {"type": None}
    if isinstance(annotation, object):  # is class
        annotation_type_class_name = getattr(type(annotation), "__name__")
        if annotation_type_class_name == "_GenericAlias":
            if getattr(annotation, "__module__") == "typing":
                if (
                    getattr(annotation, "_name") == "List"
                    or getattr(annotation, "_name") == "Dict"
                ):
                    if args := getattr(annotation, "__args__"):
                        if getattr(args[0], "__name__") == "Literal":
                            first_element = getattr(args[0], "__args__")[0]
                            literal_first_type = get_type_dict(type(first_element))
                            if literal_first_type is None:
                                raise Exception("Unsupported typing")
                            literal_first_type = literal_first_type["type"]
                            return {
                                "type": f"typing.List[{literal_first_type}]",
                                "whitelist": getattr(args[0], "__args__"),
                            }
                    return {"type": str(annotation)}
                elif (
                    str(getattr(annotation, "__origin__")) == "typing.Literal"
                ):  # Python 3.8
                    literal_first_type = get_type_dict(
                        type(getattr(annotation, "__args__")[0])
                    )
                    if literal_first_type is None:
                        raise Exception("Unsupported typing")
                    literal_first_type = get_type_dict(
                        type(getattr(annotation, "__args__")[0])
                    )["type"]
                    return {
                        "type": literal_first_type,
                        "whitelist": getattr(annotation, "__args__"),
                    }
                elif (
                    str(getattr(annotation, "__origin__")) == "typing.Union"
                ):  # typing.Optional
                    union_first_type = get_type_dict(
                        getattr(annotation, "__args__")[0]
                    )["type"]
                    return {"type": union_first_type, "optional": True}
                else:
                    raise Exception("Unsupported typing")
            else:
                raise Exception("Support typing only")
        elif annotation_type_class_name == "_LiteralGenericAlias":  # Python 3.10
            if str(getattr(annotation, "__origin__")) == "typing.Literal":
                literal_first_type = get_type_dict(
                    type(getattr(annotation, "__args__")[0])
                )["type"]
                return {
                    "type": literal_first_type,
                    "whitelist": getattr(annotation, "__args__"),
                }
            else:
                raise Exception("Unsupported annotation")
        elif annotation_type_class_name == "GenericAlias":
            if getattr(annotation, "__name__") == "list":
                return {"type": "list"}
            elif getattr(annotation, "__name__") == "dict":
                return {"type": "dict"}
            else:
                raise Exception("Unsupported annotation")
        elif annotation_type_class_name == "_SpecialGenericAlias":
            if (
                getattr(annotation, "_name") == "Dict"
                or getattr(annotation, "_name") == "List"
            ):
                return {"type": str(annotation)}
        elif annotation_type_class_name == "_TypedDictMeta":
            key_and_type = {}
            for key in annotation.__annotations__:
                key_and_type[key] = (
                    supported_basic_types_dict[annotation.__annotations__[key].__name__]
                    if annotation.__annotations__[key].__name__
                    in supported_basic_types_dict
                    else annotation.__annotations__[key].__name__
                )
            return {"type": "typing.Dict", "keys": key_and_type}
        elif annotation_type_class_name == "type":
            return {"type": getattr(annotation, "__name__")}
        elif annotation_type_class_name == "range":
            return {"type": "range"}
        elif annotation_type_class_name in ["UnionType", "_UnionGenericAlias"]:
            if (
                len(getattr(annotation, "__args__")) != 2
                or getattr(annotation, "__args__")[0].__name__ == "NoneType"
                or getattr(annotation, "__args__")[1].__name__ != "NoneType"
            ):
                raise Exception("Must be X | None, Optional[X] or Union[X, None]")
            optional_config = {"optional": True}
            optional_config.update(get_type_dict(getattr(annotation, "__args__")[0]))
            return optional_config
        else:
            # raise Exception("Unsupported annotation_type_class_name")
            return {"type": "typing.Dict"}
    else:
        return {"type": str(annotation)}


def get_type_widget_prop(
    function_arg_type_name: str,
    index: int,
    function_arg_widget: list | str,
    widget_type: dict,
    function_annotation: Parameter | Any,
) -> dict:
    """
    Mixing the five magic parameters together, you end up with RJSF-readable data.

    Parameters:
        function_arg_type_name (str): The type name of the function argument.
        index (int): Widget index (in `function_arg_widget`).
        function_arg_widget (list | str): The widget dict of the function argument.
        widget_type (dict): The widget type dict.
        function_annotation (Parameter | Any): The annotation of the function argument.

    Returns:
        dict: The RJSF-readable data.
    """
    # Basic and List only
    anal_result = analyze(function_annotation)
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
        if hasattr(function_annotation, "__name__"):
            if getattr(function_annotation, "__name__") == single_widget_type:
                widget = widget_type[single_widget_type]
                break
    if not widget:
        if hasattr(function_annotation, "__name__"):
            function_annotation_name = getattr(function_annotation, "__name__")
            if function_annotation_name == "Literal":
                widget = (
                    "radio" if len(function_annotation.__args__) < 8 else "inputbox"
                )
            elif function_annotation_name == "List" or (
                function_annotation_name == "list"
                and hasattr(function_annotation, "__args__")
            ):
                if args := getattr(function_annotation, "__args__"):
                    if getattr(args[0], "__name__") == "Literal":
                        widget = "checkbox" if len(args[0].__args__) < 8 else "inputbox"
            elif function_annotation_name in builtin_widgets:
                widget = builtin_widgets[function_annotation_name]
    if widget and anal_result:
        anal_result["widget"] = widget

    if anal_result:
        return anal_result
    if function_arg_type_name in supported_basic_types:
        return {
            "type": supported_basic_types_dict[function_arg_type_name],
            "widget": widget,
        }
    elif function_arg_type_name.startswith("range"):
        return {"type": "integer", "widget": widget}
    elif function_arg_type_name == "list":
        if type(function_annotation).__name__ == "GenericAlias" and hasattr(
            function_annotation, "__args__"
        ):
            arg = getattr(function_annotation, "__args__")[0]
            return {
                "type": "array",
                "widget": widget,
                "items": get_type_widget_prop(
                    getattr(arg, "__name__"),
                    index + 1,
                    function_arg_widget,
                    widget_type,
                    arg,
                ),
            }
        return {
            "type": "array",
            "items": {"type": "any", "widget": ""},
            "widget": widget,
        }
    else:
        typing_list_search_result = search(
            r"typing\.(?P<containerType>List)\[(?P<contentType>.*)]",
            function_arg_type_name,
        )
        if isinstance(typing_list_search_result, Match):  # typing.List, typing.Dict
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
                    function_annotation,
                ),
            }
        elif function_arg_type_name == "typing.Dict":
            return {"type": "object", "widget": widget}
        elif function_arg_type_name == "typing.List":
            return {"type": "array", "widget": widget}
        else:
            # raise Exception("Unsupported Container Type")
            return {"type": "object", "widget": widget}


def funix_param_to_widget(annotation: any) -> str:
    """
    Convert the funix parameter annotation to widget.

    Parameters:
        annotation (any): The annotation, type or something.

    Returns:
        str: The converted widget.
    """
    need_config = hasattr(annotation, "__funix_config__")
    if need_config:
        return f"{annotation.__funix_widget__}{json.dumps(list(annotation.__funix_config__.values()))}"
    else:
        return annotation.__funix_widget__


def function_param_to_widget(annotation: any, widget: str) -> any:
    """
    Convert the function parameter annotation to widget.

    Parameters:
        annotation (any): The annotation, type or something.
        widget (str): The widget name.

    Returns:
        Any: The converted widget.
    """
    if type(annotation) is range or annotation is range:
        start = annotation.start if type(annotation.start) is int else 0
        stop = annotation.stop if type(annotation.stop) is int else 101
        step = annotation.step if type(annotation.step) is int else 1
        widget = f"slider[{start},{stop - 1},{step}]"
    elif hasattr(annotation, "__funix_widget__"):
        widget = funix_param_to_widget(annotation)
    else:
        if (
            type(annotation).__name__ == "_GenericAlias"
            and annotation.__name__ == "List"
        ):
            if annotation.__args__[0] is range or type(annotation.__args__[0]) is range:
                arg = annotation.__args__[0]
                start = arg.start if type(arg.start) is int else 0
                stop = arg.stop if type(arg.stop) is int else 101
                step = arg.step if type(arg.step) is int else 1
                widget = [
                    widget if isinstance(widget, str) else widget[0],
                    f"slider[{start},{stop - 1},{step}]",
                ]
            elif hasattr(annotation.__args__[0], "__funix_widget__"):
                widget = [
                    widget if isinstance(widget, str) else widget[0],
                    funix_param_to_widget(annotation.__args__[0]),
                ]
    return widget


def get_dataframe_json(dataframe) -> dict:
    """
    Converts a pandas dataframe to a dictionary for drawing on the frontend

    Parameters:
        dataframe (pandas.DataFrame | pandera.typing.DataFrame): The dataframe to convert

    Returns:
        dict: The converted dataframe
    """
    return json.loads(dataframe.to_json(orient="records"))


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
    import matplotlib

    if __matplotlib_use:
        if mpld3 is None:
            try:
                import matplotlib.pyplot

                mpld3 = import_module("mpld3")
            except:
                raise Exception("if you use matplotlib, you must install mpld3")

        fig = mpld3.fig_to_dict(figure)
        matplotlib.pyplot.close()
        return fig
    else:
        raise Exception("Install matplotlib to use this function")


def get_figure_image(figure) -> str:
    """
    Converts a matplotlib figure to a static image for drawing on the frontend

    Parameters:
        figure (matplotlib.figure.Figure): The figure to convert

    Returns:
        str: The converted image with static URI
    """
    import matplotlib.pyplot

    matplotlib.pyplot.close()

    with io.BytesIO() as buf:
        figure.savefig(buf, format="png")
        buf.seek(0)
        return get_static_uri(buf.getvalue())


class LambdaVisitor(ast.NodeVisitor):
    def __init__(self, app_name: str, _globals: dict = None, _locals: dict = None):
        self.lambda_call_function = None
        self.args = {}
        self.app_name = app_name
        self.globals = _globals
        self.locals = _locals
        self.in_class = False
        if "_funix_self" in self.locals:
            self.locals["self"] = self.locals["_funix_self"]
            self.in_class = True

    def visit_Lambda(self, node):
        if isinstance(node.body, ast.Call):
            # I tried, this is the best way to get the call function in my test
            func_expr = ast.Expression(node.body.func)
            ast.fix_missing_locations(func_expr)
            self.lambda_call_function = eval(
                compile(func_expr, filename="<ast>", mode="eval"),
                self.globals,
                self.locals,
            )

            if self.in_class:
                self.lambda_call_function = get_class_method_funix(
                    self.app_name,
                    self.locals["self"]
                    .__class__.__dict__[self.lambda_call_function.__name__]
                    .__qualname__,
                )

            if (
                get_function_uuid_with_id(self.app_name, id(self.lambda_call_function))
                == ""
            ):
                self.lambda_call_function = None
            else:
                args = [
                    eval(
                        compile(ast.Expression(arg), filename="<ast>", mode="eval"),
                        self.globals,
                        self.locals,
                    )
                    for arg in node.body.args
                ]
                kwargs = {
                    keyword.arg: eval(
                        compile(
                            ast.Expression(keyword.value), filename="<ast>", mode="eval"
                        ),
                        self.globals,
                        self.locals,
                    )
                    for keyword in node.body.keywords
                }
                sign = signature(self.lambda_call_function)
                sign = sign.bind(*args, **kwargs)
                sign.apply_defaults()
                self.args = sign.arguments


def get_callable_result(
    app_name: str, function: Callable, function_locals: dict
) -> dict:
    if function.__name__ == "<lambda>":
        visitor = LambdaVisitor(app_name, function.__globals__, function_locals)
        visitor.visit(ast.parse(getsource(function).strip()))
        if visitor.lambda_call_function is None:
            return {"jump": "#", "title": "No jump"}
        function = visitor.lambda_call_function
        args = visitor.args
        jump_uuid = get_function_uuid_with_id(app_name, id(function))
        if jump_uuid == "":
            return {"jump": "#", "title": "No jump"}
        result = get_function_detail_by_uuid(app_name, jump_uuid)
        return {"jump": result["path"], "title": result["name"], "args": args}
    else:
        jump_uuid = get_function_uuid_with_id(app_name, id(function))
        if jump_uuid == "":
            return {"jump": "#", "title": "No jump"}
        result = get_function_detail_by_uuid(app_name, jump_uuid)
        return {"jump": result["path"], "title": result["name"]}


def anal_function_result(
    frame: Any,
    app_name: str,
    function_call_result: Any,
    return_type_parsed: Any,
    cast_to_list_flag: bool,
) -> Any:
    """
    Analyze the function result to get the frontend-readable data.

    Parameters:
        frame (Any): The frame.
        app_name (str): The app name.
        function_call_result (Any): The function call result.
        return_type_parsed (Any): The parsed return type.
        cast_to_list_flag (bool): Whether to cast the result to list.

    Returns:
        Any: The frontend-readable data.
    """
    # TODO: Best result handling, refactor it if possible
    call_result = function_call_result
    if return_type_parsed == "Figure":
        return [get_figure(call_result)]

    if return_type_parsed == "FigureImage":
        return [get_figure_image(call_result)]

    if return_type_parsed == "Dataframe":
        return [get_dataframe_json(call_result)]

    if return_type_parsed == "Callable":
        return [get_callable_result(app_name, call_result, frame.f_locals)]

    if return_type_parsed in supported_basic_file_types:
        if __ipython_use:
            if isinstance(
                call_result,
                __ipython_display.Audio
                | __ipython_display.Video
                | __ipython_display.Image,
            ):
                return [handle_ipython_audio_image_video(call_result)]
        return [get_static_uri(call_result)]
    else:
        if isinstance(call_result, list):
            return [call_result]

        if __ipython_use:
            if isinstance(
                call_result,
                __ipython_display.HTML | __ipython_display.Markdown,
            ):
                call_result = call_result.data

            if isinstance(call_result, __ipython_display.Javascript):
                call_result = (
                    "<script>"
                    + getattr(call_result, "_repr_javascript_")()
                    + "</script>"
                )

        if not isinstance(call_result, (str, dict, tuple)):
            call_result = json.dumps(call_result)

        if cast_to_list_flag:
            call_result = list(call_result)
        else:
            if isinstance(call_result, (str, dict)):
                call_result = [call_result]
            if isinstance(call_result, tuple):
                call_result = list(call_result)

        if call_result and isinstance(call_result, list):
            if isinstance(return_type_parsed, list):
                for position, single_return_type in enumerate(return_type_parsed):
                    if __ipython_use:
                        if call_result[position] is not None:
                            if isinstance(
                                call_result[position],
                                (__ipython_display.HTML, __ipython_display.Markdown),
                            ):
                                call_result[position] = call_result[position].data
                            if isinstance(
                                call_result[position], __ipython_display.Javascript
                            ):
                                call_result[position] = (
                                    "<script>"
                                    + getattr(
                                        call_result[position], "_repr_javascript_"
                                    )()
                                    + "</script>"
                                )
                            if isinstance(
                                call_result[position],
                                (
                                    __ipython_display.Audio,
                                    __ipython_display.Video,
                                    __ipython_display.Image,
                                ),
                            ):
                                call_result[
                                    position
                                ] = handle_ipython_audio_image_video(
                                    call_result[position]
                                )
                    if single_return_type == "Figure":
                        call_result[position] = get_figure(call_result[position])

                    if single_return_type == "FigureImage":
                        call_result[position] = get_figure_image(call_result[position])

                    if single_return_type == "Callable":
                        call_result[position] = get_callable_result(
                            app_name, call_result[position], frame.f_locals
                        )

                    if single_return_type == "Dataframe":
                        call_result[position] = get_dataframe_json(
                            call_result[position]
                        )

                    if single_return_type in supported_basic_file_types:
                        if isinstance(call_result[position], list):
                            if __ipython_use:
                                call_result[position] = [
                                    handle_ipython_audio_image_video(single)
                                    if isinstance(
                                        single,
                                        (
                                            __ipython_display.Audio,
                                            __ipython_display.Video,
                                            __ipython_display.Image,
                                        ),
                                    )
                                    else get_static_uri(single)
                                    for single in call_result[position]
                                ]
                            else:
                                call_result[position] = [
                                    get_static_uri(single)
                                    for single in call_result[position]
                                ]
                        else:
                            if __ipython_use:
                                call_result[position] = (
                                    handle_ipython_audio_image_video(
                                        call_result[position]
                                    )
                                    if isinstance(
                                        call_result[position],
                                        (
                                            __ipython_display.Audio,
                                            __ipython_display.Video,
                                            __ipython_display.Image,
                                        ),
                                    )
                                    else get_static_uri(call_result[position])
                                )
                            else:
                                call_result[position] = get_static_uri(
                                    call_result[position]
                                )
                return call_result
            else:
                if return_type_parsed == "Figure":
                    call_result = [get_figure(call_result[0])]
                if return_type_parsed == "FigureImage":
                    call_result = [get_figure_image(call_result[0])]
                if return_type_parsed == "Dataframe":
                    call_result = [get_dataframe_json(call_result[0])]
                if return_type_parsed == "Callable":
                    call_result = [
                        get_callable_result(app_name, call_result[0], frame.f_locals)
                    ]
                if return_type_parsed in supported_basic_file_types:
                    if isinstance(call_result[0], list):
                        if __ipython_use:
                            call_result = [
                                [
                                    handle_ipython_audio_image_video(single)
                                    if isinstance(
                                        single,
                                        (
                                            __ipython_display.Audio,
                                            __ipython_display.Video,
                                            __ipython_display.Image,
                                        ),
                                    )
                                    else get_static_uri(single)
                                    for single in call_result[0]
                                ]
                            ]
                        else:
                            call_result = [
                                [get_static_uri(single) for single in call_result[0]]
                            ]
                    else:
                        if __ipython_use:
                            call_result = [
                                handle_ipython_audio_image_video(call_result[0])
                                if isinstance(
                                    call_result[0],
                                    (
                                        __ipython_display.Audio,
                                        __ipython_display.Video,
                                        __ipython_display.Image,
                                    ),
                                )
                                else get_static_uri(call_result[0])
                            ]
                        else:
                            call_result = [get_static_uri(call_result[0])]
                return call_result
    return call_result


def parse_function_annotation(
    function_signature: Signature, figure_to_image: bool
) -> tuple[bool, Any]:
    cast_to_list_flag = False
    if function_signature.return_annotation is not Signature.empty:
        # TODO: Magic code, I've forgotten what it does, but it works, refactor it if you can
        # return type dict enforcement for yodas only
        try:
            if (
                cast_to_list_flag := function_signature.return_annotation.__class__.__name__
                == "tuple"
                or function_signature.return_annotation.__name__ == "tuple"
                or function_signature.return_annotation.__name__ == "Tuple"
            ):
                parsed_return_annotation_list = []
                if function_signature.return_annotation.__class__.__name__ == "tuple":
                    return_annotation = list(function_signature.return_annotation)
                else:
                    return_annotation = list(
                        function_signature.return_annotation.__args__
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
                        return_annotation_type_name = supported_basic_types_dict[
                            return_annotation_type_name
                        ]
                    elif return_annotation_type_name == "List":
                        list_type_name = getattr(
                            getattr(return_annotation_type, "__args__")[0],
                            "__name__",
                        )
                        if list_type_name in supported_basic_file_types:
                            return_annotation_type_name = list_type_name
                    if full_type_name in ipython_type_convert_dict:
                        return_annotation_type_name = ipython_type_convert_dict[
                            full_type_name
                        ]
                    elif full_type_name in dataframe_convert_dict:
                        return_annotation_type_name = dataframe_convert_dict[
                            full_type_name
                        ]
                    parsed_return_annotation_list.append(return_annotation_type_name)
                return_type_parsed = parsed_return_annotation_list
            else:
                if hasattr(function_signature.return_annotation, "__annotations__"):
                    return_type_raw = getattr(
                        function_signature.return_annotation, "__annotations__"
                    )
                    if getattr(type(return_type_raw), "__name__") == "dict":
                        if function_signature.return_annotation.__name__ == "Figure":
                            return_type_parsed = (
                                "Figure" if not figure_to_image else "FigureImage"
                            )
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
                                if full_name in ipython_type_convert_dict:
                                    return_type_parsed = ipython_type_convert_dict[
                                        full_name
                                    ]
                                elif full_name in dataframe_convert_dict:
                                    return_type_parsed = dataframe_convert_dict[
                                        full_name
                                    ]
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
                            getattr(function_signature.return_annotation, "__args__")[
                                0
                            ],
                            "__name__",
                        )
                        if list_type_name in supported_basic_file_types:
                            return_type_parsed = list_type_name
        except:
            return_type_parsed = get_type_dict(function_signature.return_annotation)
            if return_type_parsed is not None:
                return_type_parsed = return_type_parsed["type"]
    else:
        return_type_parsed = None
    return cast_to_list_flag, return_type_parsed
