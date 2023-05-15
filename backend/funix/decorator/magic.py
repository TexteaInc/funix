"""
Magic functions, refactor it if you can.

I can't guarantee that the type annotations and comments here are correct, because the logic and naming here is so
complex and confusing that I copied them from `decorator/__init__.py`.

The main features of the functions here are to analyze the types/annotations/parameters and return the processed data
to the frontend for direct use or as middleware to return the pre-processed data awaiting further analysis.

However, their logic is complex, with a lot of if-else, no comments and no unit tests, so it is not very good to infer
the types of parameters, the types of return values and the rough logic.
"""

import json
from inspect import Parameter
from re import Match, search
from typing import Any

from funix.config import supported_basic_types, supported_basic_types_dict


def get_type_dict(annotation: any) -> dict:
    """
    Get the type dict of the annotation.

    Parameters:
        annotation (any): The annotation for analysis.

    Examples:
        >>> import typing
        >>> from funix.decorator.magic import get_type_dict
        >>>
        >>> get_type_dict(int) == {"type": "int"}
        >>> get_type_dict(type(True)) == {"type": "bool"}
        >>> get_type_dict(typing.Literal["a", "b", "c"]) == {'type': 'str', 'whitelist': ('a', 'b', 'c')}
        >>> get_type_dict(typing.Optional[int]) == {'optional': True, 'type': 'int'}

    Returns:
        dict: The type dict.
    """
    # TODO: String magic, refactor it if you can
    if isinstance(annotation, object):  # is class
        annotation_type_class_name = getattr(type(annotation), "__name__")
        if annotation_type_class_name == "_GenericAlias":
            if getattr(annotation, "__module__") == "typing":
                if (
                    getattr(annotation, "_name") == "List"
                    or getattr(annotation, "_name") == "Dict"
                ):
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
        if function_annotation.__name__ == single_widget_type:
            widget = widget_type[single_widget_type]
            break
    if function_arg_type_name in supported_basic_types:
        return {
            "type": supported_basic_types_dict[function_arg_type_name],
            "widget": widget,
        }
    elif function_arg_type_name.startswith("range"):
        return {"type": "integer", "widget": widget}
    elif function_arg_type_name == "list":
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


def convert_row_item(row_item: dict, item_type: str) -> dict:
    """
    Convert a layout row item(block) to frontend-readable item.

    Parameters:
        row_item (dict): The row item.
        item_type (str): The item type.

    Returns:
        dict: The converted item.
    """
    converted_item = row_item
    converted_item["type"] = item_type
    converted_item["content"] = row_item[item_type]
    converted_item.pop(item_type)
    return converted_item


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
    elif hasattr(annotation, "__funix__"):
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
            elif hasattr(annotation.__args__[0], "__funix__"):
                widget = [
                    widget if isinstance(widget, str) else widget[0],
                    funix_param_to_widget(annotation.__args__[0]),
                ]
    return widget
