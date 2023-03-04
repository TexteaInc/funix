import random
from typing import List, Optional, Tuple, Literal, Union
import typing
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from funix import funix, funix_yaml, funix_json5
from funix.hint import Image, File, Markdown, HTML, Code, Video, Audio

@funix(
        show_source=True
)
def hello(name: str) -> str:
	return f"Hello, {name}."

#TODO: Bao to add a column of sliders.
@funix(
    title="Table, theme, and argument_config",
    description="""
### This example shows off multiple features of Funix. 
* Per-argument customizations are aggregated in the `argument_config` parameter. 
* Arugments (a and b here) of same configurations are configured jointly as a tuple in `argument_config`.
* The `theme` parameter is used to customize the look and widget selection of the app.
* The resulting sheet's header is set in the return `dict`. The header is _Total_ if the operator is _add_, and _Difference_ if the operator is _minus_.

### Usage of this demo
1. Select an opeartor
2. Enter two lists of numbers in the two columns of the table. Some values are prefilled. 
3. Click Submit to see the result.
4. In the Output panel, click the `Sheet` radio button to view the result as a headed table. 
    """,
    # theme = "https://raw.githubusercontent.com/TexteaInc/funix-doc/main/examples/sunset_v2.yaml", 
    theme = "./sunset_v2.yaml",
    # FIXME: this themes makes the menu over the table dissapear. 
    # Current workaround is to change the button to contained variant. 
    # A proper fix should use an outlined button with a new prop in theme file to change the color in the text and the outline/border.
    argument_config={
        "op": {
	        "argument_label": "Select an operation",
        }, 
        #FIXME: in argument_config, the key cannot be a tuple, like ("a", "b"): {"widget":"sheet", "treat_as":"column"}.
        "a": {
            "widget": "sheet"
        },
        "b": {
            "widget": "sheet"
        }
    }, 
    show_source=True
)
def calc(op: Literal["add", "minus"]="add", a: List[int]=[10,20], b: List[int]=[50,72]) -> dict:
    if op == "add":
        return {"Total": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"Difference": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise Exception("invalid parameter op")


# map via cell 


# Show all widgets
@funix(
    show_source=True,
    description="Showing off all widgets supported by Funix. Be sure to click Submit to reveal the output widgets as well. More examples at [QuickStart](https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md)",

    # we only need to customized non-default/theme widgets
    widgets={'int_input_slider': 'slider', 
             'float_input_slider': 'slider[0,10,0.1]', 
             'bool_input_switch': 'switch', 
             'literal_input_radio': 'radio', 
             'literal_input_select': 'select',
             'str_input_textarea': 'textarea', 
             'X': 'sheet', 'Z': 'sheet',
             'Y': 'sheet', }
)
def widget_showoff(
    int_input_slider: int=32, 
    float_input_slider: float=411, 
    int_input_default: int=123, 
    float_input_default: float=78.92, 
    bool_input_default: bool=True, 
    bool_input_switch: bool=True,
    literal_input_radio: typing.Literal["add", "minus"]='add',
    literal_input_select: typing.Literal["a", "b", "c"]='c',
    str_input_default: str = "All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others.", 
    str_input_textarea: str="This request may not be serviced in the Roman Province\
            of Judea due to the Lex Julia Majestatis, which disallows\
            access to resources hosted on servers deemed to be\
            operated by the People's Front of Jude",
    X: typing.List[int]=[1919, 1949, 1979, 2019],
    Y: typing.List[float]=[3.141, 2.718, 6.626, 2.997],
    Z: typing.List[str]=["Pi", "e", "Planck", "Speed of light"]
    ) -> Tuple[Markdown, str, HTML, dict, Markdown,  dict, Image, Markdown, Audio, File, List[Video] , Markdown, Figure, Code]: 

    matplotlib_figure = plt.figure()
    plt.plot(X, Y)

    sum_ = calc(op=literal_input_radio, a=X, b=Y)

    code = {
            "lang": "python",
            "code": """from funix import funix

@funix()
def hello_world(name: str) -> str:
    return f"Hello, {name}"
"""
    }

    my_dict= {"name": "Funix", 
              "Features": [
                    {"The laziest way to build apps in Python": ["Automatic UI generation from Python function signatures", "No UI code needed"]},
                    {"Partitioned": ["UI and logic are separated", "just like CSS for HTML", "or .sty in LaTeX"]}, 
                    "Scalable: Define one theme and then all variables of the same type will be in the same widget", 
                    "Declarative: You can use JSON5 and YAML to configure your widgets",
                    "Non-intrusive",
              ], 
              "version": 0.3}

    return """## [Funix.io](http://Funix.io) _supports_ ~~Markdown~~! <br> Basic return types like integers or strings are not displaye here because they are obviously easy to support. We will display complex ones. """, \
        f"The sum of the first two numbers in the input panels is {int_input_slider + float_input_slider}", \
        "<span style='color: blue'>JSON or dict returns can be rendered using our our sister project <a href='https://github.com/TexteaInc/json-viewer'>JSON-viewer!</a>. See the rendering results below </span>", \
        my_dict, \
        "### The sum of the X and Y columns in the input table is below. Be sure to use check the `Sheet` radio to view the result in a single-column sheet.", \
        sum_, \
        "https://opengraph.githubassets.com/1/TexteaInc/Json-viewer", \
        "### Your function can return **video, image, audio, and binary files** and Funix will add a player/downloader for you.", \
        "http://curiosity.shoutca.st:8019/128", \
        "https://github.com/TexteaInc/funix-doc/blob/main/illustrations/workflow.png?raw=true",\
        ["http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4", "https://user-images.githubusercontent.com/438579/219586150-7ff491dd-dfea-41ea-bfad-4610abf1fe20.mp4"], \
        """### You can also return matplotlib plots and code blocks! The plot below is generated from data in the sheet at the bottom of the input (left) panel. """, \
        matplotlib_figure, \
        code
        

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
    ],
    title="Guess Number",
    path="guess"
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

# Plot and paste 
@funix(
    widgets = {
        ("X", "Z"): ["sheet"],
        "Y": ["sheet", "slider[0, 1, 0.01]"]
    }
)
def plot_test(X: List[int], Y: List[float], Z: List[bool]) -> Figure:
    fig = plt.figure()
    plt.plot(X, Y)
    return fig

# conditional visibility

# layout 

# multi-page, a non-AI simple one 

# AI 


@funix(
    widgets={
        ("phrase", "year", "freq", "test"): "sheet"
    }
)
def sheet_trim(phrase: List[str], year: List[int], freq: List[int], test: List[str]) -> Figure:
    fig = plt.figure()
    plt.plot(year, freq)
    return fig
