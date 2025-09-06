# Embedding an EPAM Ketcher chemistry drawer as the input and return the InChi, SMILES, and SVG-format structure of the substance you just draw.


from typing import Tuple

from IPython.display import Markdown

from funix.hint import Ketcher, ChemStr
from funix import funix




@funix()
def Ketcher_demo(x: Ketcher) -> Tuple[Markdown, ChemStr]:
    markdown = f"""The substance you just drew, has the following:
* InChi: {x.inchi}
* SMILES: {x.smiles}"""

    return markdown, x.smiles
