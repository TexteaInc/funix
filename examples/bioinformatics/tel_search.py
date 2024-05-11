# Copyright 2022 Forrest Sheng Bao forrestbao.github.io
# This script detects whether a string is a telomere.
# For the definition of telomere, please refer to 
# https://en.wikipedia.org/wiki/Telomere
# To see usage, go to test() function at the end

#%% 
import math
import hashlib
import typing
import functools
import multiprocessing

import pandas, pandera

import funix

#%%

@funix.funix(disable=True)
def reverse_complement(s:str):
    mapping = {"A":"T", "G":"C", "C":"G", "T":"A"}
    reverse = "".join([mapping.get(s0) for s0 in s])
    return reverse[::-1]

#%%
@funix.funix(disable=True)
def gen_telomeres_forward(repeat, length:int=21):

    """Generate telomeres from a repeat

    repeat: str, the sequence whose shifted repeats become a telomere
    length: int, the length of shifted repeats
    """
    
    cycles = length // len(repeat) + 2
    base_string = repeat * cycles 

    telomeres = [base_string[i: i + length ] for i in range(len(repeat))]
    # telomeres = [i for i in range(len(repeat))]

    # print (base_string)

    return telomeres

@funix.funix(disable=True)
def gen_telomeres(repeat, length=21, include_reverse:bool=True):
    """Generate telomeres from a repeat
    
    repeat: str, the sequence whose shifted repeats become a telomere
    length: int, the length of shifted repeats
    include_reverse: boolean, whether to use the reverse complement of repeat to generate telomeres too. 
    """

    telomeres = gen_telomeres_forward(repeat, length=length)
    
    if include_reverse:
        telomeres += gen_telomeres_forward(reverse_complement(repeat), length=length)

    return telomeres

@funix.funix(disable=True)
def get_telomere_hash_dict(repeat, include_reverse:bool=True):
    """Return the hash dictionary of telomeres 

    return dict, key as length (int) and values as hash values for all telomeres of the length. 
    """
    telomere_hash_dict = {}
    for i in range(20, 25+1):
        telomeres_local = gen_telomeres(repeat, length=i, include_reverse=include_reverse)
        telomeres_local_hashes = [hashlib.sha256(t.encode('utf-8')).hexdigest() for t in telomeres_local]
        telomere_hash_dict[i] = telomeres_local_hashes

    return telomere_hash_dict

@funix.funix(disable=True)
def search_string_hash(pattern:str, telomere_hash_dict) -> bool:
    """Determine whether a string is a telomere of given  repeat
    """

    # print (len(pattern))

    if len(pattern) < 20 or len(pattern) > 25:
        return False 

    hashes_local = telomere_hash_dict[len(pattern)]
    # list

    pattern_hash = hashlib.sha256(pattern.encode('utf-8')).hexdigest()

    for i in hashes_local:
        if pattern_hash == i:
            return True
    return False

# %%
@funix.funix(disable=True)
def search_telomeres(sRNAs:typing.List[str], repeat:str, include_reverse:bool=True) -> typing.List[bool]:
    """Determine whether a list of strings are telomers of the given repeat 
    """

    print (sRNAs)

    telomere_hash_dict = get_telomere_hash_dict(repeat, include_reverse=include_reverse)

    func_search_one_pattern = functools.partial(search_string_hash, telomere_hash_dict=telomere_hash_dict)

    # with multiprocessing.Pool() as pool:
    #     result = pool.map(func_search_one_pattern, sRNAs)
    result = list(map(func_search_one_pattern, sRNAs))

    print (result )

    return result

# %%
@funix.funix(disable=True)
def test():
    sRNAs = ['CCCTAAACCCTAAACCCTAT',  # False
             'CCCTAAACCCTAAACCCTAA',   # True, 20-nt 
             'CCCTAAACCCTAAACCC',    # False , too short 
            'CCCTAAACCCTAAACCCTAAAC', # True, 22-nt
            'CTAAACCCTAAACCCTAAACCCT' # True, 22-nt
    ]
    repeat = "CCCTAAA"

    return search_telomeres(sRNAs, repeat)


class InputSchema(pandera.DataFrameModel):
    sRNAs: pandera.typing.Series[str]


@funix.funix(
    description = "A telomere is a region of repetitive DNA sequences at the end of a chromosome. Enter a repeating unit, and a list of sRNAs in the table below, this telomere checker will tell whether each of the sRNAs is a telomere.",
    # destination = "column",
    # argument_config = {
    #     "sRNAs": {
    #         "widget" : "sheet"
    #     },    
    #     "repeat_unit": {
    #         # "treat_as": "config",
    #         "examples": ["CCCTAAA"]
    #     }
    # }
)
def telomere_check(
    # sRNAs: typing.List[str] = [
    #     "CCCTAAACCCTAAACCCTAT",  # False
    #     "CCCTAAACCCTAAACCCTAA",  # True, 20-nt
    #     "CCCTAAACCCTAAACCC",  # False, too short
    #     "CCCTAAACCCTAAACCCTAAAC",  # True, 22-nt
    #     "CTAAACCCTAAACCCTAAACCCT"  # True, 25-nt
    # ],    
    sRNAs: pandera.typing.DataFrame[InputSchema] =
        pandas.DataFrame({"sRNAs": 
        [
            "CCCTAAACCCTAAACCCTAT",  # False
            "CCCTAAACCCTAAACCCTAA",  # True, 20-nt
            "CCCTAAACCCTAAACCC",  # False, too short
            "CCCTAAACCCTAAACCCTAAAC",  # True, 22-nt
            "CTAAACCCTAAACCCTAAACCCT"  # True, 25-nt
        ]
        }),
    repeat_unit: str="CCCTAAA"
    # ) -> typing.Dict[str, bool]: 
    # check_result = search_telomeres(sRNAs, repeat_unit)
    # return {"sRNAs":sRNAs, "Is it a telemere?":check_result }

    ) -> pandas.DataFrame:
    check_result = search_telomeres(sRNAs["sRNAs"].tolist(), repeat_unit)
    return pandas.DataFrame({"sRNAs":sRNAs["sRNAs"], "Is it a telemere?":check_result })


if __name__ == '__main__':
    print (test())
