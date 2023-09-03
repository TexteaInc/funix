import random, os, typing
from typing import List, Tuple, Literal

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from funix import funix
from funix.hint import Image, File, Markdown, HTML, Code, Video, Audio
from funix.widget import slider


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
    widgets={
        ("a", "b", "c"): "sheet",
    },
    argument_config={
        "op": {
            "label": "Select an operation",
        },
    },
    show_source=True,
)
def calc(
    op: Literal["add", "minus"] = "add",
    a: List[int] = [10, 20],
    b: List[int] = [50, 72],
    c: List[bool] = [True, False],
) -> dict:
    if op == "add":
        return {"Total": [a[i] + b[i] for i in range(min(len(a), len(b)))]}
    elif op == "minus":
        return {"Difference": [a[i] - b[i] for i in range(min(len(a), len(b)))]}
    else:
        raise Exception("invalid parameter op")



# Per OpenAI's documentation,
# https://platform.openai.com/docs/guides/chat/introduction
# The main input is the messages parameter. Messages must be an array of message objects, where each object has a role (either "system", "user", or "assistant") and content (the content of the message). Conversations can be as short as 1 message or fill many pages.
