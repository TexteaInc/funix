# Default and example values for variables

import typing
import funix 

@funix.funix(
    description="This example shows how to provide argument/input values that users can select from in the UI. Simpliy taking advantage of Python's default values for keyword arguments, Literal type in type hints, and the `example` parameter in Funix. ",
    examples={"arg3": [1, 5, 7]},
    widgets={"arg2": "radio"},
    show_source=True,
)
def default_and_candidate_values(
    arg1: str = "prime",
    arg2: typing.Literal["is", "is not"]="is",
    arg3: int = 3,
) -> str:
    return f"The number {arg3} {arg2} {arg1}."