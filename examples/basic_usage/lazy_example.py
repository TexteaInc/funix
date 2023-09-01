def hello(name: str) -> str:
    return f"Hello {name}!"


def calc(a: int, b: int, op: str) -> int:
    return a + b if op == "add" else a - b
