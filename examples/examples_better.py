from pydatafront.decorator import funix_export


@funix_export(
    widgets={
        "switch": ["arg1"]
    },
    treat_as={
        "column": ["arg2"],
    },
    whitelist={
        "arg2": ["a", "b", "c"]
    }
)
def elegant(arg1: bool, arg2: str) -> dict:
    return {
        "arg1": arg1,
        "arg2": arg2
    }

@funix_export(
    labels={
        "input1": "Reactant 1",
        "input2": "Reactant 2",
        "output": "Resultant",
        "condition": "Reaction Condition",
        "extra": "Whether the resultant is a gas or not (the reactant has no gas)"
    },
    whitelist={
        "condition": ["Heating", "High Temperature", "Electrolysis"]
    },
    widgets={
        "switch": ["extra"]
    },
)
def chemist(
    input1: str = "S",
    input2: str = "O₂",
    output: str = "SO₂",
    condition: str = "Heating",
    extra: bool = False
) -> str:
    return f"{input1} + {input2} --{condition}-> {output}{'↑' if extra else ''}"
