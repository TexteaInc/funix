# Copyright 2022 Forrest Sheng Bao forrestbao.github.io
# This script removes adapters in RNA-seqs
# To see usage, go to test() function at the end

import typing
import functools
import multiprocessing

import pandas, pandera

import funix

@funix.funix(disable=True)
def remove_3_prime_adapter_one(
    sRNA: str = "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT",
    adapter_3_prime: str = "TCGTATGCCGTCTTCTGCTT",
    minimal_match_length: int = 0,
    verbose_level: int = 1,
):
    """Use reverse shift to match the sRNA with the 3' adapter
    minimal_match_length: the sRNA needs at least that much matchness
    with the 3' adapter to be considered valid.
    verbose_level = 0, 1, 2. O means no details. 1: show final alignment per sequence. 2: show aligment at every step.
    Example:
        sRNA = AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT
        adapter_3_prime = TCGTATGCCGTCTTCTGCTT
    """

    return_code = -1  # 1: found. 0: match to short. -1: no match at all.
    return_seq = "no match at all"

    # check whether the 3' adapter is fully enclosed in sRNA
    i = sRNA.find(adapter_3_prime)

    if i > -1:
        return_code, return_seq = 1, sRNA[:i]
        print(sRNA, "\n", " " * (i - 1) + adapter_3_prime)
    else:
        for i in range(len(adapter_3_prime)):
            sRNA_tail = sRNA[-1 * i :]
            adapter_3_prime_head = adapter_3_prime[:i]
            if verbose_level == 2:
                print(sRNA, "\n", adapter_3_prime_head.rjust(len(sRNA) - 1))
            if sRNA_tail == adapter_3_prime_head:
                if i + 1 > minimal_match_length:
                    return_code = 1
                    return_seq = sRNA[: -1 * i]
                    if verbose_level == 1:
                        print(sRNA, "\n", adapter_3_prime_head.rjust(len(sRNA) - 1))
                    break
                else:
                    return_code, return_seq = 0, f"match <{minimal_match_length} nts"

    return return_code, return_seq


@funix.funix(disable=True)
def remove_3_prime_adapter_vectorized(
    sRNAs: typing.List[str] = [
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGC",  # shorter than full 3' adapter
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT",  # full 3' adapter
        "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTTCTGAATTAATT",  # additional seq after 3' adapter,
        "AAGCTCAGGAGGGATAGCGCCTCGTATG",  # <8 nt io 3' adapter
        "AAGCTCAGGAGGGATAGCGCCGTATG",  # no match at all
    ],
    adapter_3_prime: str = "TCGTATGCCGTCTTCTGCTT",
    minimal_match_length: int = 8,
    verbose_level: int = 1,
):
    # print (adapter_3_prime)

    func_remove_3_prime_adapter_partial = functools.partial(
        remove_3_prime_adapter_one,
        adapter_3_prime=adapter_3_prime,
        minimal_match_length=minimal_match_length,
        verbose_level=1,
    )

    # with multiprocessing.Pool() as pool:
    #     result = pool.map(func_remove_3_prime_adapter_partial, sRNAs)
    # BUG: Not a priority. Funix cannot work with multiprocessing. The two lines above will throw an error. But there is no problem to run this script locally.
    # Comment: I won't fix multiprocessing issue now.
    result = list(map(func_remove_3_prime_adapter_partial, sRNAs))

    returns = list(zip(*result))
    # print (returns)
    [return_codes, return_seqs] = returns

    return return_codes, return_seqs

@funix.funix(disable=True)
def test():
    return_codes, return_seqs = remove_3_prime_adapter_vectorized()  # all default value
    for code, seq in zip(return_codes, return_seqs):
        print(code, ":", seq)


class InputSchema(pandera.DataFrameModel):
    sRNAs: pandera.typing.Series[str]


class OutputSchema(pandera.DataFrameModel):
    original_sRNA: pandera.typing.Series[str]
    adapter_removed: pandera.typing.Series[str]


@funix.funix(
    description="Remove 3' prime adapter from the end of an RNA-seq",
)
def remove_3_prime_adapter(
    # adapter_3_prime: str="TCGTATGCCGTCTTCTGCTT",
    adapter_3_prime: str = "TCGTA",
    minimal_match_length: int = 8,
    sRNAs: pandera.typing.DataFrame[InputSchema] = pandas.DataFrame(
        {
            "sRNAs": [
                "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGC",  # shorter than full 3' adapter
                "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTT",  # full 3' adapter
                # additional seq after 3' adapter,
                "AAGCTCAGGAGGGATAGCGCCTCGTATGCCGTCTTCTGCTTCTGAATTAATT",
                "AAGCTCAGGAGGGATAGCGCCTCGTATG",  # <8 nt io 3' adapter
                "AAGCTCAGGAGGGATAGCGCCGTATG",  # no match at all
            ]
        }
    ),
    # ) -> pandera.typing.DataFrame[OutputSchema]:
) -> pandas.DataFrame:
    return_codes, return_seqs = remove_3_prime_adapter_vectorized(
        sRNAs=sRNAs["sRNAs"].tolist(),
        adapter_3_prime=adapter_3_prime,
        minimal_match_length=minimal_match_length,
    )
    return pandas.DataFrame(
        {"original sRNA": sRNAs["sRNAs"], "adapter removed": list(return_seqs)}
    )


if __name__ == "__main__":
    test()
