import random
from typing import List, Tuple
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from funix import funix, funix_yaml, funix_json5
from funix.hint import Images, Files, Markdown, HTML, Code, Videos, Audios


@funix(
    widgets={
        "arg1": "switch"
    },
    treat_as={
        "arg2": "column"
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

@funix(
    widgets={
        "location": "radio"
    },
    whitelist={
        "location": [
            "Ibaraki", "Tochigi", "Saitama", "Chiba",
            "Tokyo", "Kanagawa", "Yamanashi"
        ]
    },
    argument_labels={
        "location": "Location",
    }
)
def shuto_ken(location: str) -> str:
    return location

@funix(
    argument_labels={
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
        "extra": "switch"
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

@funix(
    description="Guess Number: Input two numbers, and the program will calculate the average of them. If the average "
                "number is program's guess number, you win! Otherwise, you lose.",
    argument_labels={
        "input1": "Number 1",
        "input2": "Number 2",
        "show": "Show me the number 😭"
    },
    widgets={
        "show": "switch",
        ("input1", "input2"): "slider[0, 100]"
    },
    input_layout=[
        [{"markdown": "**Guess Number**"}],
        [
            {"argument": "input1", "width": 6},
            {"argument": "input2", "width": 6}
        ],
        [{"dividing": "Cheat Option", "position": "left"}],
        [{"argument": "show", "width": 12}]
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

@funix(
    description="Input github repo url, get the banner and zip download link.",
    argument_labels={
      "url": "GitHub Repo URL"
    },
    output_layout=[
        [{"markdown": "**Banner**"}],
        [{"return": 0}],
        [{"dividing": True}],
        [{"markdown": "**Download Link**"}],
        [{"return": 1}],
    ]
)
def github_banner(url: str) -> Tuple[Images, Files]:
    author = url.split("/")[3]
    name = url.split("/")[4]
    return f"https://opengraph.githubassets.com/1/{author}/{name}", f"{url}/archive/refs/heads/main.zip"

@funix(
    argument_config={
        "test": {
            "treat_as": "config",
            "widget": "switch"
        }
    }
)
def argument_config(test: bool) -> dict:
    return {
        "test": test
    }

@funix(
    widgets={
        "arg1": ["sheet", "slider"],
        "arg2": ["sheet", "slider"]
    }
)
def slider_in_sheet(arg1: List[int] = [10, 32], arg2: List[int] = [35]) -> dict:
    return {
        "arg1": arg1,
        "arg2": arg2
    }

@funix(
    examples={
        ("test", "test2"): [
            ["hello", "hi"],
            ["world", "funix"]
        ]
    }
)
def greet(test: str, test2: str) -> str:
    return f"{test} {test2}"

@funix(
    widgets = {
        "year": ["sheet"],
        "period": ["sheet", "slider[0, 1, 0.01]"]
    },
    treat_as={
        ("year", "period"): "column"
    }
)
def plot_test(year: List[int], period: List[float]) -> Figure:
    fig = plt.figure()
    plt.plot(year, period)
    return fig

@funix(
    widgets = {
        "more_config": "switch"
    },
    conditional_visible = [
        {
            "if": {"more_config": True},
            "then": ["arg1", "arg2"]
        }
    ]
)
def if_then(
    more_config: bool,
    arg1: str = "None",
    arg2: str = "None"
) -> dict:
    return {
        "arg1": arg1,
        "arg2": arg2
    }

@funix_yaml("""
argument_labels:
    arg1: isGood
widgets:
    arg1: switch
""")
def yaml_export(arg1: bool = False) -> dict:
    return {
        "arg1": arg1
    }

@funix_json5("""
{
    "argument_labels": {
        "arg1": "isGood"
    },
    "widgets": {
        "arg1": "switch"
    }
}
""")
def json_export(arg1: bool = False) -> dict:
    return {
        "arg1": arg1
    }

@funix()
def more_return() -> Tuple[str, int, dict, Figure, Figure]:
    first_figure = plt.figure()
    plt.plot([1, 2, 3], [4, 5, 6])
    second_figure = plt.figure()
    plt.plot([7, 8, 9], [12, 11, 10])
    return "hello", 1, {"hello": "world"}, first_figure, second_figure

@funix()
def more_more_return() -> Tuple[Markdown, HTML]:
    return "**This is ~~Markdown~~**", "<span style='color: blue'>This is HTML</span>"

@funix()
def media_return() -> Tuple[Images, Videos, Audios]:
    return "https://opengraph.githubassets.com/1/TexteaInc/Json-viewer", \
        ["http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4", "https://www.w3schools.com/html/movie.mp4"], \
        "http://curiosity.shoutca.st:8019/128"

@funix()
def file_return() -> Tuple[Files, Code]:
    return "https://github.com/TexteaInc/funix/archive/refs/heads/main.zip", \
        {
            "lang": "python",
            "code": """from funix import funix

@funix()
def hello_world(name: str) -> str:
    return f"Hello, {name}"
"""
        }


@funix()
def local_return() -> Tuple[Images, Files]:
    return "./files/test.png", "./files/test.txt"


@funix(
    output_layout=[
        [{"code": "return 'Hello'"}],
        [{"code": "const fn = () => 'Hello'"}],
    ]
)
def code_return() -> str:
    return "Test"

@funix(
    show_source_code = True
)
def show_source_code() -> str:
    return "Hello World"
