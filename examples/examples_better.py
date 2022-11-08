import random
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
    }
)
def chemist(
    input1: str = "S",
    input2: str = "O₂",
    output: str = "SO₂",
    condition: str = "Heating",
    extra: bool = False
) -> str:
    return f"{input1} + {input2} --{condition}-> {output}{'↑' if extra else ''}"

randomNumber = (random.randint(0, 100) + random.randint(0, 100)) / 2

@funix_export(
    description="Guess Number: Input two numbers, and the program will calculate the average of them. If the average number is program's guess number, you win! Otherwise, you lose.",
    labels={
        "input1": "Number 1",
        "input2": "Number 2",
        "show": "Show me the number 😭"
    },
    widgets={
        "switch": ["show"],
        "slider[0, 100]": ["input1", "input2"]
    },
    layout=[
        [{"type": "markdown", "content": "**Guess Number**"}],
        [
            {"type": "argument", "argument": "input1", "width": 6},
            {"type": "argument", "argument": "input2", "width": 6}
        ],
        [{"type": "dividing", "content": "Cheat Option", "position": "left"}],
        [{"type": "argument", "argument": "show", "width": 12}],
        [{"type": "html", "content": "<span>Have Fun!</span>"}]
    ]
)
def guess(
    input1: int = 0,
    input2: int = 0,
    show: bool = False
) -> str:
    global randomNumber
    if show:
        return f"The number is {randomNumber}"
    else:
        if (input1 + input2) / 2 == randomNumber:
            result = f"You win! The number is {randomNumber}. And random number is reset."
            randomNumber = (random.randint(0, 100) + random.randint(0, 100)) / 2
            return result
        else:
            if (input1 + input2) / 2 > randomNumber:
                return "Bigger"
            else:
                return "Smaller"
