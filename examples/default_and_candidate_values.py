# Default and example values for variables

import typing
import funix 

@funix.funix(
    description="This example shows how to provide default and candiadate/example values for UI widgets. For default values, simpliy take advantage of Python's default value syntax for keyword arguments. For example values, use the `example` parameter in Funix. ",
    examples={"arg3": [1, 5, 7]},
    show_source=True,
)
def default_and_candidate_values(
    arg1: str = "Default value prefilled. ",
    arg2: typing.Literal["is", "is not"]="is not",
    arg3: int = 3,
) -> str:
    return f"The number {arg3} {arg2} {arg1}."