from funix.hint import Ketcher
from funix import funix


@funix()
def chem_test(x: Ketcher) -> str:
    return x.inchi
