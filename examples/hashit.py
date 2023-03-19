import hashlib
from typing import List
from funix import funix
from funix.widget.builtin import BytesFile


@funix(
    title="Get Files SHA256",
)
def hashit(datas: List[BytesFile]) -> list:
    results = []
    for data in datas:
        sha256 = hashlib.sha256()
        sha256.update(data)
        results.append(sha256.hexdigest())
    return results

