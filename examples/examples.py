from funix import funix
from typing import List, TypedDict, Dict


@funix()
def hello(name: str) -> str:
	return f"Hello, {name}."

@funix(
    path="cell_test",
    description="painful",
    argument_config={
        "a": {
            "treat_as": "cell",
            "widget": ["sheet"]
        },
        "b": {
            "treat_as": "cell",
            "widget": ["sheet"]
        },
        "isAdd": {
            "treat_as": "config",
            "widget": ["switch"]
        }
    }
)
def cell_test(a: int, b: int, isAdd: bool) -> int:
    return a + b if isAdd else a - b

@funix(
    path="json_editor",
    description="config only",
    argument_config={
        "config_dict": {
            "treat_as": "config",
            "widget": ["json"]
        },
        "config_list": {
            "treat_as": "config",
            "widget": ["json"]
        }
    }
)
def json_editor(config_dict: Dict, config_list: List[str]) -> dict:
    return {
        "dict": config_dict,
        "list": config_list
    }


class Person(TypedDict):
    name: str
    age: int
    isAdult: bool


@funix(
    path="json_editor_better",
    description="list and typed_dict",
    argument_config={
        "config_typed_dict": {
            "treat_as": "config",
            "widget": ["json"]
        },
        "config_list": {
            "treat_as": "config",
            "widget": ["json"]
        }
    }
)
def json_editor_better(config_typed_dict: Person, config_list: List) -> dict:
    return {
        "typed": config_typed_dict,
        "list": config_list
    }




class add_with_sub_return(TypedDict):
    add: List[int]
    sub: List[int]


# only supported by Funix
@funix(
    path="nested-array",
    argument_config={
        "a": {
            "treat_as": "column"
        }
    }
)
def nested_array(a: List[List[int]]):
    return {
        "output": str(a)
    }


# transform test
# just create a new sheet of two columns of integers, regardless of the input
@funix(
    destination="sheet"
)
def transform_test(a: List[int]):
    return {"column1": [1, 2, 3],
            "column2": [4, 5, 6]}


@funix()
def empty():
    pass
