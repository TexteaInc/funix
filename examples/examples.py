from pydatafront.decorator import textea_export
from typing import List, TypedDict

import tel_search


class telomere_check_return(TypedDict):
    is_telomere: List[bool]


@textea_export(path='bioinfo_telomere_check',
               sRNAs={'treat_as': 'column',
                      'example':
                          [
                              ['CCCTAAACCCTAAACCCTAT',  # False
                               'CCCTAAACCCTAAACCCTAA',  # True, 20-nt
                               'CCCTAAACCCTAAACCC',  # False, too short
                               'CCCTAAACCCTAAACCCTAAAC',  # True, 22-nt
                               'CTAAACCCTAAACCCTAAACCCT'  # True, 25-nt
                               ]
                          ]
                      },
               repeat_unit={'treat_as': 'config',
                            'example': ["CCCTAAA"]
                            }
               )
def bioinfo_telomere_check(sRNAs: List[str], repeat_unit: str) -> telomere_check_return:
    check_result = tel_search.search_telomeres(sRNAs, repeat_unit)
    return {'is_telomere': check_result}


class calc_return(TypedDict):
    output: List[int]


@textea_export(
    path='calc',
    type={
        'whitelist': ['add', 'minus'],
        'treat_as': 'config'
    },
    a={
        'treat_as': 'column'
    },
    b={
        'treat_as': 'column'
    }
)
def calc(a: List[int], b: List[int], type: str) -> calc_return:
    if type == 'add':
        return {'output': [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif type == 'minus':
        return {'output': [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise 'invalid parameter type'


@textea_export(
    path='calc_add',
    a={
        'treat_as': 'column'
    },
    b={
        'treat_as': 'column'
    }
)
def calc_add(a: List[int], b: List[int]) -> calc_return:
    return calc(a, b, 'add')


class add_with_sub_return(TypedDict):
    add: List[int]
    sub: List[int]


@textea_export(
    path='owo',
    a={
        'treat_as': 'column'
    },
    b={
        'treat_as': 'column'
    }
)
def add_with_sub(a: List[int], b: List[int]) -> add_with_sub_return:
    return {
        'add': [a[i] + b[i] for i in range(min(len(a), len(b)))],
        'sub': [a[i] - b[i] for i in range(min(len(a), len(b)))],
    }
