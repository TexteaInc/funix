from funix import funix


def add(a: int, b: int) -> int:
    return a + b


@funix(reactive={"c": add})
def add_reactive(a: int, b: int, c: int) -> int:
    return a + b + c
