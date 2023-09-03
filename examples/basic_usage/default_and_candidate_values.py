# Default, choices, and example values

import funix 

@funix.funix(
    title="Let users select",
    description="This example shows how to provide argument/input values that users can select from in the UI. Simpliy taking advantage of Python's default values for keyword arguments, Literal type in type hints, and the `example` parameter in Funix. ",
    examples={"arg1": [1, 5, 7]},
    widgets={"arg2": "radio"},
    show_source=True,
)
def argument_selection(
    arg1: int,
    arg2: typing.Literal["is", "is not"],
    arg3: str = "prime",
) -> str:
    return f"The number {arg1} {arg2} {arg3}."