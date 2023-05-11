import random, os, typing
from typing import List, Tuple, Literal

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from funix import funix, import_theme
from themes.better import indian_red, textbook, hokusai
from funix.hint import Image, File, Markdown, HTML, Code, Video, Audio
from funix.widget import slider

import_theme(alias="indian_red", module=indian_red)
import_theme(alias="textbook", module=textbook)
import_theme(alias="hokusai", module=hokusai)


@funix(
    show_source=True,
)
def hello(name: str = "NCC-1701") -> str:
    return f"Hello, {name}."


@funix(
    title="Table and argument_config",
    description="""
### This example shows off multiple features of Funix. Click `Source Code` to see the code.
* Per-argument customizations are aggregated in the `argument_config` parameter.
* Parameter keys are tuples to configure multiple arguments altogether in a batch.
* The resulting sheet's header is set in the return `dict`. The header is _Total_ if the operator is _add_, and _Difference_ if the operator is _minus_.

### Enjoy this demo
1. Select an opeartor, add or minus.
2. Use the sliders to adjust the numbers in any cell.
3. To add rows, click the `Add a Row` button.
4. Click Submit to see the result.
5. In the Output panel, click the `Sheet` radio button to view the result as a headed table.
    """,
    # theme="https://raw.githubusercontent.com/TexteaInc/funix-doc/main/examples/sunset_v2.yaml",
    # theme = "葛飾 北斎",
    widgets={
        ("a", "b", "c"): "sheet",
    },
    argument_config={
        "op": {
            "label": "Select an operation",
        },
    },
    show_source=True
)
def calc(
    op: Literal["add", "minus"] = "add",
    a: List[int] = [10, 20],
    b: List[int] = [50, 72],
    c: List[bool] = [True, False]
) -> dict:
    if op == "add":
        return {"Total": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"Difference": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise Exception("invalid parameter op")


# map via cell

@funix(
    title="""Automatic vectorization""",
    description="""Funix automatically vectorizes a scalar function on arguments declared to be cells in a sheet. See the source code for details. In this example, arguments `a` and `b` are declared so and hence the function is partially mapped onto them -- partial because the argument `isAdd` is not declared so. **Usage:** Simply click 'Add a row' button to create new rows and then double-click cells to add numeric values. Run, and in the output panel, click the `Sheet` radio button to view the result as a headed table.""",
    widgets={
        ("a", "b"): "sheet",
    },
    treat_as={
        ("a", "b"): "cell"
    },
    show_source=True
)
def cell_test(a: int, b: int, isAdd: bool) -> int:
    return a + b if isAdd else a - b


# Show all widgets
@funix(
    title="All widgets",
    description="Showing off all widgets supported by Funix. *Be sure to click Run to reveal the output widgets.* CLick `Source Code` to see the mapping from each input/output type to a widget. Most widgets here are determined by the default theme. Only a handful of them are customized in the `widgets` parameter in the `@funix` decorator.  More examples at [QuickStart](https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md)",

    # we only need to customized non-default/theme widgets
    widgets={'int_input_slider': slider(),
             'float_input_slider': slider(0, 500, 0.1),
             'bool_input_switch': 'switch',
             'literal_input_radio': 'radio',
             'literal_input_select': 'select',
             'str_input_textarea': 'textarea',
             ('X', 'Y', 'Z'): 'sheet'},
    show_source=True
)
def widget_showoff(
    int_input_slider: int = 32,
    float_input_slider: float = 411,
    int_input_default: int = 123,
    float_input_default: float = 78.92,
    bool_input_default: bool = True,
    bool_input_switch: bool = True,
    literal_input_radio: typing.Literal["add", "minus"] = 'add',
    literal_input_select: typing.Literal["a", "b", "c"] = 'c',
    str_input_default: str = "All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others.",
    str_input_textarea: str = "This request may not be serviced in the Roman Province\
            of Judea due to the Lex Julia Majestatis, which disallows\
            access to resources hosted on servers deemed to be\
            operated by the People's Front of Jude",
    X: typing.List[int] = [1919, 1949, 1979, 2019],
    Y: typing.List[float] = [3.141, 2.718, 6.626, 2.997],
    Z: typing.List[str] = ["Pi", "e", "Planck", "Speed of light"]
) -> Tuple[
    Markdown, str, Markdown, Audio, File, List[Video], HTML, dict, Image, Markdown, dict, Markdown, Figure, Code]:
    matplotlib_figure = plt.figure()
    plt.plot(
        range(1, 50),
        [random.random() for i in range(1, 50)],
        'r-'
    )
    plt.plot(
        range(1, 50),
        [random.random() for i in range(1, 50)],
        'k--'
    )

    sum_ = calc(op=literal_input_radio, a=X, b=Y)
    code_content = """
from funix import funix

@funix()
def hello_world(name: str) -> str:
    return f"Hello, {name}"
""".strip()

    code = {
        "lang": "python",
        "code": code_content
    }

    my_dict = {"name": "Funix",
               "Features": [
                   {"The laziest way to build apps in Python": [
                       "Automatic UI generation from Python function signatures", "No UI code needed"]},
                   {"Partitioned": ["UI and logic are separated", "just like CSS for HTML", "or .sty in LaTeX"]},
                   "Scalable: Define one theme and then all variables of the same type will be in the same widget",
                   "Declarative: You can use JSON5 and YAML to configure your widgets",
                   "Non-intrusive",
               ],
               "version": 0.3}

    return """
## Output widgets supported by [Funix.io](http://Funix.io)
Basic types like _int_ or _str_ are for sure. **Markdown** or `HTML` strings are automatically rendered. But it does more, including tables, video players, Matplotlib plots, and the tree views of JSON strings.
""", \
        f"The sum of the first two numbers in the input panels is {int_input_slider + float_input_slider}", \
        "### Funix will add a player/downloader for multimedia and binary file returns. ", \
        "http://curiosity.shoutca.st:8019/128", \
        "https://github.com/TexteaInc/funix-doc/blob/main/illustrations/workflow.png?raw=true", \
        ["http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4",
         "https://user-images.githubusercontent.com/438579/219586150-7ff491dd-dfea-41ea-bfad-4610abf1fe20.mp4"], \
        "<span style='color: blue'>JSON or dict returns can be rendered using our our sister project <a href='https://github.com/TexteaInc/json-viewer'>JSON-viewer!</a>. See the rendering results below </span>", \
        my_dict, \
        "https://opengraph.githubassets.com/1/TexteaInc/Json-viewer", \
        "### Results from table operations can be rendered as tables or JSON. The sum of the X and Y columns in the input table is below. Be sure to check the `Sheet` radio to view the result in a single-column sheet.", \
        sum_, \
        """### You can also return matplotlib plots and code blocks! """, \
        matplotlib_figure, \
        code


randomNumber = random.randint(0, 100)


@funix(
    title="Number guessing",
    description="The program has a random integer between 0 and 100 in its mind. You play the game by entering two numbers and the average of them will be used to guess the random number. If the average of your two numbers equals to the random number in the program's mind, you win! Otherwise, you will be instructed to guess bigger or smaller next time. Of course, you can cheat by togging the `Let me cheat` switch.",
    argument_labels={
        "input1": "Number 1",
        "input2": "Number 2",
        "cheat": "Let me cheat 😭"
    },
    widgets={
        "show": "switch",
        ("input1", "input2"): slider(0, 100)
    },
    input_layout=[
        [{"markdown": "**Guess a number**"}],
        [
            {"argument": "input1", "width": 6},
            {"argument": "input2", "width": 6}
        ],
        [{"dividing": "Cheat Option", "position": "left"}],
        [{"argument": "cheat", "width": 12}]
    ],
    show_source=True,
)
def guess(
    input1: int = 0,
    input2: int = 0,
    cheat: bool = False
) -> str:
    global randomNumber
    if cheat:
        result = f"The number is {randomNumber}. And it has been reset."
        randomNumber = random.randint(0, 100)
        return result
    else:
        if (input1 + input2) / 2 == randomNumber:
            result = f"You won! The number was {randomNumber}. And it has been reset."
            randomNumber = random.randint(0, 100)
            return result
        else:
            if (input1 + input2) / 2 > randomNumber:
                return "Try smaller. "
            else:
                return "Try bigger. "


# Default, choices, and example values

@funix(
    title="Let users select",
    description="This example shows how to provide argument/input values that users can select from in the UI. Simpliy taking advantage of Python's default values for keyword arguments, Literal type in type hints, and the `example` parameter in Funix. ",
    examples={"arg1": [1, 5, 7]},
    widgets={"arg2": "radio"},
    show_source=True
)
def argument_selection(
    arg1: int,
    arg2: typing.Literal["is", "is not"],
    arg3: str = "prime",
) -> str:
    return f"The number {arg1} {arg2} {arg3}."


# Plot and paste
@funix(
    description="Visualize two columns of a table, where the two columns use different input UIs: numeric input boxes and sliders, resepctively.",
    widgets={
        "a": "sheet",
        "b": ["sheet", slider(0, 1, 0.01)]
    },
    show_source=True
)
def slider_table_plot(
    a: List[int] = list(range(30)),
    b: List[float] = [random.random() for _ in range(30)]
) -> Figure:
    fig = plt.figure()
    plt.plot(a, b)
    return fig


# conditional visibility

# simple layout 
@funix(
    input_layout=[
        [{'dividing': "Funix rocks!"}],  # row 1
        [{"argument": "x", "width": 4},
         {"argument": "y", "width": 4}],  # row 2
    ],
    output_layout=[
        [{"markdown": "**First return**"}, {"index": 0}],  # row 1
        [{"markdown": "**Second return**"}, {"index": 1}]  # row 2
    ]
)
def simple_layout(x: int, y: int) -> (int, int):
    return x + y, x - y


# layout
@funix(
    title="Layout Example",
    description="This example create a card for a Github repo based on the user name and repo name. The purpose of this example is to show how to customize the layout in a row-based grid approach.",
    # argument_labels={
    #   "user_name": "username",
    # },
    input_layout=[
        [{"html": "https://github.com/", "width": 3.5},
         {"argument": "user_name", "width": 4},
         {"html": "/", "width": 0.2},
         {"argument": "repo_name", "width": 4}, ]
        # all in row 1
    ],
    output_layout=[
        [{"index": 0}],  # row 1
        [{"markdown": "**Download Link**", "width": 2},
         {"index": 1}],  # row 2
        [{"markdown": "**Visit the repo**"},
         {"index": 2}]  # row 3
    ],
    show_source=True
)
def layout_example(user_name: str = "texteainc",
                   repo_name: str = "json-viewer") -> (Image, File, Markdown):
    url = f"https://github.com/{user_name}/{repo_name}"
    author = url.split("/")[3]
    name = url.split("/")[4]
    return f"https://opengraph.githubassets.com/1/{author}/{name}", \
        f"{url}/archive/refs/heads/main.zip", \
        f"[{url}]({url})"


# multi-page, a non-AI simple one
haha = "hello"


@funix(
    title="Multipage: Page 1",
    description="""
This demo shows how to pass data between pages.

It's very simple. Each page is a Funix-decorated function. So just use a global variable to pass data between pages.

Another example is OpenAI demos where OpenAI key is set in one page while DallE and GPT3 demos use the key in other pages. Check them out using the function selector above""",
    argument_labels={"x": "New value for `haha`"},
    show_source=True
)
def set_value_here(x: str) -> Markdown:
    global haha
    haha = x
    return f"The value of `haha` has been set to **{haha}**. Now check its value in 'Multipage: Page 2'. It should have already been changed."


@funix(
    title="Multipage: Page 2",
    description="""
**Run 'Multiplage: Page 1' first**.

Click the Run button to get the value of the variable `haha` set in 'Multipage: Page 1'. Default value of `haha` is 'hello'. """,
    show_source=True
)
def get_value_here() -> Markdown:
    return f"the value of `haha` is **{haha}**."


# AI

import openai  # pip install openai

openai.api_key = os.environ.get("OPENAI_KEY")


@funix(  # Funix.io, the laziest way to build web apps in Python
    title="OpenAI: Dall-E",
    description="""Generate an image by prompt with DALL-E.""",
    widgets={"openai_key": "password"},
    conditional_visible=[
        {"all_if": {"show_advanced": True, },
         "then": ["openai_key"]}
    ],
    show_source=True
)
def dalle(
    Prompt: str = "a cat on a red jeep",
    openai_key: str = "",
) -> Image:
    if openai_key != "":
        openai.api_key = openai_key

    response = openai.Image.create(prompt=Prompt)
    return response["data"][0]["url"]


@funix(
    description="""Try the **ChatGPT** app in [Funix](http://funix.io)""",
    argument_labels={
        "prompt": "_What do you wanna ask?_",
        "max_tokens": "**Length** of the answer",
        "show_advanced": "Show advanced options",
        "openai_key": "Use your own OpenAI key",
        "model": "Choose a model",
    },
    widgets={"openai_key": "password", "model": "radio",
             "show_advanced": "checkbox", "show_verbose": "switch"},
    conditional_visible=[
        {"all_if": {"show_advanced": True, },
         "then": ["max_tokens", "model", "openai_key"]}
    ],
    show_source=True
)
def ChatGPT(prompt: str,
            model: typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0301'] = 'gpt-3.5-turbo',
            max_tokens: range(20, 100, 20) = 80,
            openai_key: str = "",
            show_advanced: bool = False,
            ) -> str:
    if openai_key != "":
        openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]

# Per OpenAI's documentation, 
# https://platform.openai.com/docs/guides/chat/introduction
# The main input is the messages parameter. Messages must be an array of message objects, where each object has a role (either "system", "user", or "assistant") and content (the content of the message). Conversations can be as short as 1 message or fill many pages.
