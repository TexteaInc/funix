
import typing, random
import matplotlib.figure, matplotlib.pyplot
import funix 

def calc(
    op: typing.Literal["add", "minus"] = "add",
    a: typing.List[int] = [10, 20],
    b: typing.List[int] = [50, 72],
    c: typing.List[bool] = [True, False],
) -> dict:
    if op == "add":
        return {"Total": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"Difference": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise Exception("invalid parameter op")

# Show all widgets
@funix.funix(
    title="All widgets",
    description="Showing off all widgets supported by Funix. *Be sure to click Run to reveal the output widgets.* CLick `Source Code` to see the mapping from each input/output type to a widget. Most widgets here are determined by the default theme. Only a handful of them are customized in the `widgets` parameter in the `@funix` decorator.",
    # we only need to customized non-default/theme widgets
    widgets={
        "int_input_slider": "slider",
        "float_input_slider": "slider[0, 500, 0.1]",
        "bool_input_switch": "switch",
        "literal_input_radio": "radio",
        "literal_input_select": "select",
        "str_input_textarea": "textarea",
        ("X", "Y", "Z"): "sheet",
    },
    show_source=True,
)
def widget_showoff(
    int_input_slider: int = 32,
    float_input_slider: float = 411,
    int_input_default: int = 123,
    float_input_default: float = 78.92,
    bool_input_default: bool = True,
    bool_input_switch: bool = True,
    literal_input_radio: typing.Literal["add", "minus", "multiply", "divide"] = "add",
    literal_input_select: typing.Literal["a", "b", "c"] = "c",
    str_input_default: str = "All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others. All animals are equal, but some animals are more equal than others.",
    str_input_textarea: str = "This request may not be serviced in the Roman Province\
            of Judea due to the Lex Julia Majestatis, which disallows\
            access to resources hosted on servers deemed to be\
            operated by the People's Front of Jude",
    X: typing.List[int] = [1919, 1949, 1979, 2019],
    Y: typing.List[float] = [3.141, 2.718, 6.626, 2.997],
    Z: typing.List[str] = ["Pi", "e", "Planck", "Speed of light"],
) -> typing.Tuple[
    funix.hint.Markdown,
    str,
    funix.hint.Markdown,
    funix.hint.Audio,
    funix.hint.File, 
    typing.List[funix.hint.Video],
    funix.hint.HTML,
    dict,
    funix.hint.Image,
    funix.hint.Markdown,
    dict,
    funix.hint.Markdown,
    matplotlib.figure.Figure,
    funix.hint.Code,
]:
    matplotlib_figure = matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(range(1, 50), [random.random() for i in range(1, 50)], "r-")
    matplotlib.pyplot.plot(range(1, 50), [random.random() for i in range(1, 50)], "k--")

    sum_ = calc(op=literal_input_radio, a=X, b=Y)
    code_content = """
from funix import funix

@funix()
def hello_world(name: str) -> str:
    return f"Hello, {name}"
""".strip()

    code = {"lang": "python", "code": code_content}

    my_dict = {
        "name": "Funix",
        "Features": [
            {
                "The laziest way to build apps in Python": [
                    "Automatic UI generation from Python function signatures",
                    "No UI code needed",
                ]
            },
            {
                "Partitioned": [
                    "UI and logic are separated",
                    "just like CSS for HTML",
                    "or .sty in LaTeX",
                ]
            },
            "Scalable: Define one theme and then all variables of the same type will be in the same widget",
            "Declarative: You can use JSON5 and YAML to configure your widgets",
            "Non-intrusive",
        ],
        "version": 0.3,
    }

    return (
        """
## Output widgets supported by [Funix.io](http://Funix.io)
Basic types like _int_ or _str_ are for sure. **Markdown** or `HTML` strings are automatically rendered. But it does more, including tables, video players, Matplotlib plots, and the tree views of JSON strings.
""",
        f"The sum of the first two numbers in the input panels is {int_input_slider + float_input_slider}",
        "### Funix will add a player/downloader for multimedia and binary file returns. ",
        "http://curiosity.shoutca.st:8019/128",
        "https://github.com/TexteaInc/funix-doc/blob/main/illustrations/workflow.png?raw=true",
        [
            "http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4",
            "https://user-images.githubusercontent.com/438579/219586150-7ff491dd-dfea-41ea-bfad-4610abf1fe20.mp4",
        ],
        "<span style='color: blue'>JSON or dict returns can be rendered using our our sister project <a href='https://github.com/TexteaInc/json-viewer'>JSON-viewer!</a>. See the rendering results below </span>",
        my_dict,
        "https://opengraph.githubassets.com/1/TexteaInc/Json-viewer",
        "### Results from table operations can be rendered as tables or JSON. The sum of the X and Y columns in the input table is below. Be sure to check the `Sheet` radio to view the result in a single-column sheet.",
        sum_,
        """### You can also return matplotlib plots and code blocks! """,
        matplotlib_figure,
        code,
    )