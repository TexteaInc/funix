from typing import List, TypedDict, Optional

import tel_search
from pydatafront.decorator import textea_export


class telomere_check_return(TypedDict):
    is_telomere: List[bool]


@textea_export(path="bioinfo_telomere_check",
               description="A telomere is a region of repetitive DNA sequences at the end of a chromosome. Find the belongings of a repeat unit.",
               sRNAs={"treat_as": "column",
                      "example":
                          [
                              ["CCCTAAACCCTAAACCCTAT",  # False
                               "CCCTAAACCCTAAACCCTAA",  # True, 20-nt
                               "CCCTAAACCCTAAACCC",  # False, too short
                               "CCCTAAACCCTAAACCCTAAAC",  # True, 22-nt
                               "CTAAACCCTAAACCCTAAACCCT"  # True, 25-nt
                               ]
                          ]
                      },
               repeat_unit={"treat_as": "config",
                            "example": ["CCCTAAA"]
                            }
               )
def bioinfo_telomere_check(sRNAs: List[str], repeat_unit: str) -> telomere_check_return:
    check_result = tel_search.search_telomeres(sRNAs, repeat_unit)
    return {"is_telomere": check_result}


class calc_return(TypedDict):
    output: List[int]


@textea_export(
    path="calc",
    description="perform some basic math calculation",
    op={
        "whitelist": ["add", "minus"],
        "treat_as": "config"
    },
    a={
        "treat_as": "column"
    },
    b={
        "treat_as": "column"
    }
)
def calc(a: List[int], b: List[int], op: str) -> calc_return:
    if op == "add":
        return {"output": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"output": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise "invalid parameter op"


@textea_export(
    path="calc_add",
    description="add two column",
    a={
        "treat_as": "column"
    },
    b={
        "treat_as": "column"
    }
)
def calc_add(a: List[int], b: List[int]) -> calc_return:
    return calc(a, b, "add")


@textea_export(
    path="calc_default_add",
    description="operate two columns with default add",
    a={
        "treat_as": "column"
    },
    b={
        "treat_as": "column"
    },
    op={
        "treat_as": "config"
    }
)
def calc_default_add(a: List[int], b: List[int], op: Optional[str] = "add") -> calc_return:
    return calc(a, b, op)


class add_with_sub_return(TypedDict):
    add: List[int]
    sub: List[int]


@textea_export(
    path="owo",
    a={
        "treat_as": "column"
    },
    b={
        "treat_as": "column"
    }
)
def add_with_sub(a: List[int], b: List[int]) -> add_with_sub_return:
    return {
        "add": [a[i] + b[i] for i in range(min(len(a), len(b)))],
        "sub": [a[i] - b[i] for i in range(min(len(a), len(b)))],
    }
