import tel_search
import vector_strip
from funix.decorator import funix
from typing import List, TypedDict, Literal, Dict


@funix()
def hello_world(your_name: str) -> str:
    return f"Welcome to Funix, {your_name}!"


class telomere_check_return(TypedDict):
    is_telomere: List[bool]


@funix(
    path = "bioinfo_telomere_check",
    description = "A telomere is a region of repetitive DNA sequences at the end of a chromosome. "
                "Find the belongings of a repeat unit.",
    destination = "column",
    argument_config = {
        "sRNAs": {
            "treat_as": "column",
            "example": [
                [
                    "CCCTAAACCCTAAACCCTAT",  # False
                    "CCCTAAACCCTAAACCCTAA",  # True, 20-nt
                    "CCCTAAACCCTAAACCC",  # False, too short
                    "CCCTAAACCCTAAACCCTAAAC",  # True, 22-nt
                    "CTAAACCCTAAACCCTAAACCCT"  # True, 25-nt
                ]
            ]
        },
        "repeat_unit": {
            "treat_as": "config",
            "example": ["CCCTAAA"]
        }
    }
)
def bioinfo_telomere_check(sRNAs: List[str], repeat_unit: str) -> telomere_check_return:
    check_result = tel_search.search_telomeres(sRNAs, repeat_unit)
    return {"is_telomere": check_result}


class remove_3_prime_adapter_return(TypedDict):
    removal_result_sequence: List[str]
    # removal_result_code: List[int]


@funix(
    path = "bioinfo_remove_3_prime_adapter",
    description = "Remove 3' prime adapter from the end of an RNA-seq",
    argument_config = {
        "sRNAs": {
            "treat_as": "column",
            "example": [
                [
                    "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGC",  # shorter than full 3' adapter
                    "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT",  # full 3' adapter
                    # additional seq after 3' adapter,
                    "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTTCTGAATTAATT",
                    "AAGCTCAGGAGGGATAGCGCCTCGTATG",  # <8 nt io 3' adapter
                    "AAGCTCAGGAGGGATAGCGCCGTATG"  # no match at all
                ]
            ]
        },
        "adapter_3_prime": {
            "treat_as": "config",
            "example": ["TCGTATGCCGTCTTCTGCTT"]
        },
        "minimal_match_length": {
            "treat_as": "config",
            "example": [6]
        }
    }
)
def bioinfo_remove_3_prime_adapter(
    sRNAs: List[str],
    adapter_3_prime: str,
    minimal_match_length: int
) -> remove_3_prime_adapter_return:
    return_codes, return_seqs = vector_strip.remove_3_prime_adapter_vectorized(
        sRNAs=sRNAs,
        adapter_3_prime=adapter_3_prime,
        minimal_match_length=minimal_match_length)
    return {"removal_result_sequence": return_seqs}
    # return {"removal_result_code": return_codes, "removal_result_sequence":return_seqs}


class calc_return(TypedDict):
    output: List[int]


# "whitelist" field is deprecated
@funix(
    path="calc",
    description="perform some basic math calculation",
    argument_config={
        "op": {
            "whitelist": ["add", "sub"],
            "treat_as": "config"
        },
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column"
        }
    }
)
def calc(a: List[int], b: List[int], op: str) -> calc_return:
    if op == "add":
        return {"output": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"output": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise "invalid parameter op"


@funix(
    path="switch_and_checkbox",
    description="just switch and checkbox",
    argument_config={
        "a": {
            "treat_as": "config",
            "widget": "switch"
        },
        "b": {
            "treat_as": "config",
            "widget": "checkbox"
        }
    }
)
def switch_and_checkbox(a: bool, b: bool) -> dict:
    return {
        "result": {
            "switch": a,
            "checkbox": b
        }
    }


@funix(
    path="slider_test",
    description="all you need is slider!",
    argument_config={
        "a": {
            "treat_as": "column",
            "widget": ["simple", "slider[0, 100, 5]"]
        },
        "b": {
            "treat_as": "config",
            "widget": ["slider[0, 100.0]"]
        }
    }
)
def slider_test(a: List[int], b: float) -> dict:
    return {
        "a": a,
        "b": b
    }


@funix(
    path="sheet_test",
    description="sweet sheet",
    argument_config={
        "a": {
            "treat_as": "column",
            "widget": ["sheet", "slider"]
        },
        "b": {
            "treat_as": "column",
            "widget": ["sheet", "switch"]
        }
    }
)
def sheet_test(a: List[int], b: List[bool]) -> dict:
    return {
        "a": a,
        "b": b
    }


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
    path="markdown_support",
    description="**Markdown** *text* `is` ~~cool~~ right?",
    argument_config={
        "cool": {
            "treat_as": "config",
            "widget": "checkbox"
        }
    }
)
def markdown_support(cool: bool) -> dict:
    return {
        "isCool": cool
    }


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


@funix(
    path="calc_literal",
    description="perform some basic math calculation",
    argument_config={
        "op": {
            "treat_as": "config"
        },
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column"
        }
    }
)
def calc_literal(a: List[int], b: List[int], op: Literal["add", "minus"]) -> calc_return:
    return calc(a, b, op)


@funix(
    path="calc_add",
    description="add two column",
    argument_config={
        "a": {
            "treat_as": "column",
            "widget": ["sheet"]
        },
        "b": {
            "treat_as": "column",
            "widget": ["sheet"]
        }
    }
)
def calc_add(a: List[int], b: List[int]) -> calc_return:
    return calc(a, b, "add")


@funix(
    path="calc_default_add",
    description="operate two columns with default add",
    argument_config={
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column"
        },
        "op": {
            "treat_as": "config"
        }
    }
)
def calc_default_add(a: List[int], b: List[int], op: str = "add") -> calc_return:
    return calc(a, b, op)


@funix(
    path="calc_boolean_add",
    description="operate two columns with boolean add",
    argument_config={
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column"
        },
        "op": {
            "treat_as": "config"
        }
    }
)
def calc_boolean_add(a: List[int], b: List[int], add: bool) -> calc_return:
    if add:
        return calc(a, b, "add")
    else:
        return calc(a, b, "minus")


@funix(
    description="operate two columns with boolean add with mixed list widgets",
    argument_config={
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column",
            "widget": ["sheet"]
        },
        "add": {
            "treat_as": "config"
        }
    }
)
def calc_boolean_mixed_add(a: List[int], b: List[int], add: bool = True) -> calc_return:
    if add:
        return calc(a, b, "add")
    else:
        return calc(a, b, "minus")


@funix(
    description="add two column with example and whitelist",
    argument_config={
        "a": {
            "treat_as": "column",
            "example": [[1, 2, 3], [4, 5, 6]],
            "widget": ["sheet"]
        },
        "b": {
            "treat_as": "column",
            "whitelist": [[7, 8, 9], [-1, -2, -3]],
            "widget": ["sheet"]
        }
    }
)
def calc_add_example_whitelist(a: List[int], b: List[int]) -> calc_return:
    return calc(a, b, "add")


class add_with_sub_return(TypedDict):
    add: List[int]
    sub: List[int]


@funix(
    path="owo",
    argument_config={
        "a": {
            "treat_as": "column"
        },
        "b": {
            "treat_as": "column"
        }
    }
)
def add_with_sub(a: List[int], b: List[int]) -> add_with_sub_return:
    return {
        "add": [a[i] + b[i] for i in range(min(len(a), len(b)))],
        "sub": [a[i] - b[i] for i in range(min(len(a), len(b)))],
    }


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
