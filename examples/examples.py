from typing import List, TypedDict, Optional

import tel_search, vector_strip
from pydatafront.decorator import textea_export


class telomere_check_return(TypedDict):
    is_telomere: List[bool]


@textea_export(path="bioinfo_telomere_check",
               description="A telomere is a region of repetitive DNA sequences at the end of a chromosome. Find the belongings of a repeat unit.",
               destination="column",
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

class remove_3_prime_adapter_return(TypedDict):
    removal_result_sequence: List[str]
    # removal_result_code: List[int]

@textea_export( path='bioinfo_remove_3_prime_adapter',
                description="Remove 3' prime adapter from the end of an RNA-seq",
                sRNAs={'treat_as':'column',
                       'example': [
                           ["AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGC", # shorter than full 3' adapter
                             "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT", # full 3' adapter
                             "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTTCTGAATTAATT", # additional seq after 3' adapter, 
                             "AAGCTCAGGAGGGATAGCGCCTCGTATG", # <8 nt io 3' adapter
                             "AAGCTCAGGAGGGATAGCGCCGTATG" # no match at all
                           ]
                       ]
                    }, 
                adapter_3_prime={'treat_as':'config', 
                                 'example': ["TCGTATGCCGTCTTCTGCTT"]
                               }, 
                minimal_match_length={'treat_as':'config', 'example':[6]}
               )
def bioinfo_remove_3_prime_adapter(sRNAs: List[str], adapter_3_prime: str, minimal_match_length:int) -> remove_3_prime_adapter_return:
    return_codes, return_seqs = vector_strip.remove_3_prime_adapter_vectorized(
                                    sRNAs=sRNAs, 
                                    adapter_3_prime=adapter_3_prime, 
                                    minimal_match_length=minimal_match_length)

    print ("hello, world")

    return {"removal_result_sequence":return_seqs}
    # return {"removal_result_code": return_codes, "removal_result_sequence":return_seqs}


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
