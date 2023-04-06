import pandas as pd
from funix import funix
from io import StringIO
from funix.hint import BytesFile

def do_calc(a: int, b: int, op: str) -> int:
    return a + b if op == "add" else a - b


@funix()
def csv_in(csv_bytes: BytesFile) -> list:
    df = pd.read_csv(StringIO(csv_bytes.decode()))
    arguments = df.values.tolist()
    return [do_calc(*arg) for arg in arguments]
