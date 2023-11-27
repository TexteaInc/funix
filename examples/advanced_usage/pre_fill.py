from funix import funix

# This example shows how to plug in results on one page to the input widgets of another. 


@funix()
def foo(x: int) -> int:
    return x - 1


@funix()
def bar(message: str) -> list[str]:
    return message.split(" ")


@funix()
def goh(x: int, y: int) -> dict:
    return {"x": x, "y": y}


@funix(
    pre_fill={
        "a": foo, # plug the return of function foo to a  
        "b": (bar, -1),  # plug the last (-1) return of function bar to b
        "c": (goh, "x")} # plug the return of key "x" of function goh to c
    )
def together(a: int, b: str, c: int) -> str:
    return f"{a} {b} {c}"
