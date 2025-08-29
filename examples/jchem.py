import requests
from funix.hint import ChemStr, Ketcher, Markdown
from typing import List, Tuple
import json

def __data_to_complex(data: List[dict]) -> List[Tuple[Markdown, ChemStr]]:
    processed = []
    for item in data:
        markdown = f"""## {item['molecule']}

```json
{json.dumps(item['additionalData'], indent=2, ensure_ascii=False)}
```
        """
        
        chemstr = item["molecule"]
        processed.append((markdown, chemstr))
    return processed

def similarity(
    structure: Ketcher,
    similarity_threshold: float = 0.8,
    hit_count: int = 10,
    filter_tolds: List[int] = [],
    timeout_in_milliseconds: int = 1000
) -> List[Tuple[Markdown, ChemStr]]:
    params = {
        "structure": structure.smiles,
        "similarityThreshold": similarity_threshold,
        "hitCount": hit_count,
    }
    if filter_tolds:
        params["filterTolds"] = filter_tolds
    if timeout_in_milliseconds:
        params["timeoutInMilliseconds"] = timeout_in_milliseconds
        
    response = requests.get(
        "https://jchem-microservices.chemaxon.com/jwsdb/rest-v1/db/additional/demoTable/similarity",
        params=params,
    )
    data = response.json()
    return __data_to_complex(data)

def substructure(
    structure: Ketcher,
    hit_count: int = 10,
    with_fingerprint_distance: bool = False,
    stereo_search_on_marked_double_bond_only: bool = False,
    stereo_search_ingore_tetrahedral_stereo: bool = False,
    ignore_charge: bool = False,
    ignore_isotope: bool = False,
    filter_tolds: List[int] = [],
    timeout_in_milliseconds: int = 1000
) -> List[Tuple[Markdown, ChemStr]]:
    params = {
        "structure": structure.smiles,
        "hitCount": hit_count,
        "withFingerprintDistance": with_fingerprint_distance,
        "stereoSearchOnMarkedDoubleBondOnly": stereo_search_on_marked_double_bond_only,
        "stereoSearchIgnoreTetrahedralStereo": stereo_search_ingore_tetrahedral_stereo,
        "ignoreCharge": ignore_charge,
        "ignoreIsotope": ignore_isotope,
    }
    if filter_tolds:
        params["filterTolds"] = filter_tolds
    if timeout_in_milliseconds:
        params["timeoutInMilliseconds"] = timeout_in_milliseconds
        
    response = requests.get(
        "https://jchem-microservices.chemaxon.com/jwsdb/rest-v1/db/additional/demoTable/substructure",
        params=params,
    )
    data = response.json()
    return __data_to_complex(data)
