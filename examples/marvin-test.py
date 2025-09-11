import os
from funix.hint import ChemStr, KetcherPopup

def ketcher_demo(ketcher: KetcherPopup) -> ChemStr:
    return ketcher.inchi
