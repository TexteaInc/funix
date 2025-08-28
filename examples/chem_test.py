from funix.hint import Ketcher, ChemStr
from funix import funix


@funix()
def chem_test(x: Ketcher) -> ChemStr:
    return x.inchi
