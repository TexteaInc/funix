import funix 


@funix.funix()
def foo_default(x:int) -> str: 
    return f"{x} appears to the row, default"

@funix.funix(
    direction="column"
)
def foo_bottom(x:int) -> str: 
    return f"{x} appears at the bottom"

@funix.funix(
    direction="column-reverse"
)
def foo_top(x:int) -> str: 
    return f"{x} appears at the top"

@funix.funix(
    direction="row-reverse"
)
def foo_left(x:int) -> str: 
    return f"{x} appears to the left"    