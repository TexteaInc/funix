from typing import Literal, TypedDict, List

from funix import funix_yaml


class TypedDictExample(TypedDict):
    a: str
    b: int


@funix_yaml()
def all_defaults(
    this_is_int: int = 42,
    this_is_float: float = 3.14,
    this_is_str: str = "This is Funix",
    this_is_bool: bool = True,
    this_is_list: List[str] = ["Funix", "Now", "这就是 Funix"],
    this_is_literal: Literal["a", "b", "c"] = "a",
    this_is_typed_dict: TypedDictExample = {
        "a": "hello",
        "b": 123,
    },
    this_is_list_python: list = ["hello", "world"],
    this_is_dict_python: dict = {"你好": "世界"},
) -> dict:
    return {
        "int": this_is_int,
        "float": this_is_float,
        "str": this_is_str,
        "bool": this_is_bool,
        "list": this_is_list,
        "literal": this_is_literal,
        "typed_dict": this_is_typed_dict,
        "list_python": this_is_list_python,
        "dict_python": this_is_dict_python,
    }

@funix_yaml("""
widgets:
  this_is_slider_1: slider
  this_is_slider_2: slider[0, 100, 0.1]
  this_is_switch: switch
  this_is_simple: simple
  this_is_sheet:
    - sheet
    - slider
  this_is_json: json
""")
def all_options(
    this_is_slider_1: int = 42,
    this_is_slider_2: float = 42,
    this_is_switch: bool = True,
    this_is_simple: List[int] = [11, 34],
    this_is_sheet: List[int] = [42, 21],
    this_is_json: List[int] = [54, 32]
) -> dict:
    return {
        "slider_1": this_is_slider_1,
        "slider_2": this_is_slider_2,
        "switch": this_is_switch,
        "simple": this_is_simple,
        "sheet": this_is_sheet,
        "json": this_is_json
    }
