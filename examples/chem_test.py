from funix import new_funix_type, funix
from IPython.display import Markdown

@new_funix_type(
    widget={
        "name": "chem"
    }
)
class ChemRaw(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smiles = self.get("smiles")
        self.inchi = self.get("inchi", None)
        self.inchi_aux_info = self.get("inchiAuxInfo", None)
        self.inchi_key = self.get("inchiKey", None)
        self.smarts = self.get("smarts")
        self.ket = self.get("ket")
        self.svg = self.get("svg")

@funix()
def chem_test(x: ChemRaw) -> Markdown:
    print(x)
    return Markdown(f"""Smiles: `{x.smiles}`\n\nInchi: `{x.inchi}`\n\nInchiAuxInfo: `{x.inchi_aux_info}`\n\nInchiKey: `{x.inchi_key}`\n\nSmarts: `{x.smarts}`\n\nKet:\n\n```json\n{x.ket}\n```\n\nSVG:\n\n```svg\n{x.svg}\n```""")
