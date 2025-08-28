# Plot the 2D structure of a chemical compound given its InChI or SMILES


from funix.hint import ChemStr
from funix import funix

@funix(
    examples={
        "inchi_or_smiles": [
            "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
            "O=C(C)Oc1ccccc1C(=O)O"
        ]
    }
)
def inchi_or_smiles_to_structure(inchi_or_smiles: str) -> ChemStr:
    return inchi_or_smiles
