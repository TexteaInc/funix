from funix import funix


@funix()
def first_action(x: int) -> int:
    return x - 1


@funix()
def second_action(message: str) -> list[str]:
    return message.split(" ")


@funix()
def third_action(x: int, y: int) -> dict:
    return {"x": x, "y": y}


@funix(
    pre_fill={
        "a": first_action, 
        "b": (second_action, -1), 
        "c": (third_action, "x")}
    )
def final_action(a: int, b: str, c: int) -> str:
    return f"{a} {b} {c}"
