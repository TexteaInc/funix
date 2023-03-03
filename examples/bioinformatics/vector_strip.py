# Copyright 2022 Forrest Sheng Bao forrestbao.github.io
# This script removes adapters in RNA-seqs 
# To see usage, go to test() function at the end

import typing
import functools
import multiprocessing


#%% 
def remove_3_prime_adapter(
    sRNA:str="AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT", 
    adapter_3_prime:str =         "TCGTATGCCGTCTTCTGCTT", 
    minimal_match_length=0, 
    verbose_level:int=1):
    """Use reverse shift to match the sRNA with the 3' adapter
    minimal_match_length: the sRNA needs at least that much matchness 
    with the 3' adapter to be considered valid. 
    verbose_level = 0, 1, 2. O means no details. 1: show final alignment per sequence. 2: show aligment at every step. 
    Example: 
        sRNA = AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT
        adapter_3_prime = TCGTATGCCGTCTTCTGCTT
    """

    return_code = -1 # 1: found. 0: match to short. -1: no match at all.
    return_seq = "no match at all"

    # check whether the 3' adapter is fully enclosed in sRNA
    i = sRNA.find(adapter_3_prime)

    if i > -1: 
        return_code, return_seq = 1, sRNA[:i]
        print (sRNA, "\n",  " "*(i-1) + adapter_3_prime)
    else :
        for i in range(len(adapter_3_prime)):
            sRNA_tail = sRNA[-1*i:]
            adapter_3_prime_head = adapter_3_prime[:i]
            if verbose_level == 2: 
                print (sRNA, "\n", adapter_3_prime_head.rjust(len(sRNA)-1))
            if sRNA_tail == adapter_3_prime_head:
                if i+1 > minimal_match_length:
                    return_code = 1
                    return_seq = sRNA[:-1*i]
                    if verbose_level ==1:
                        print (sRNA, "\n", adapter_3_prime_head.rjust(len(sRNA)-1))
                    break 
                else:
                    return_code, return_seq = 0, f"match <{minimal_match_length} nts"

    return return_code, return_seq

def remove_3_prime_adapter_vectorized(
    sRNAs:typing.List[str]=[
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGC", # shorter than full 3' adapter
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT", # full 3' adapter
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTTCTGAATTAATT", # additional seq after 3' adapter, 
        "AAGCTCAGGAGGGATAGCGCCTCGTATG", # <8 nt io 3' adapter
        "AAGCTCAGGAGGGATAGCGCCGTATG", # no match at all
    ],     
    adapter_3_prime: str =   "TCGTATGCCGTCTTCTGCTT", 
    minimal_match_length=8, 
    verbose_level = 1):

    func_remove_3_prime_adapter_partial = functools.partial(remove_3_prime_adapter, 
    adapter_3_prime=adapter_3_prime, minimal_match_length=minimal_match_length,
    verbose_level=1)

    with multiprocessing.Pool() as pool:
        result = pool.map(func_remove_3_prime_adapter_partial, sRNAs)

    print (result)
    returns =  list(zip(*result))
    # print (returns)
    [return_codes, return_seqs] = returns
    
    print (return_seqs)

    return return_codes, return_seqs

def test():
    return_codes, return_seqs = remove_3_prime_adapter_vectorized() # all default value
    for code, seq in zip(return_codes, return_seqs):
        print (code, ":", seq)


@funix(
    path = "bioinfo_remove_3_prime_adapter",
    description = "Remove 3' prime adapter from the end of an RNA-seq",
    argument_config = {
        "sRNAs": {
            "treat_as": "column",
            "examples": [
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
            "examples": ["TCGTATGCCGTCTTCTGCTT"]
        },
        "minimal_match_length": {
            "treat_as": "config",
            "examples": [6]
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


if __name__ == "__main__":
    test()

# %%