import typing 

import ipywidgets

import funix

# @funix.funix(
#     widgets={
#         "model": "input"
#     }
# )

@funix.funix(
    show_source=True,
)
def input_widgets_basic(
    prompt: str, 
    advanced_features: bool = True,
    model: typing.Literal['GPT-3.5', 'GPT-4.0', 'Falcon-7B']= 'GPT-4.0',
    max_token: range(100, 200, 20)=140,
    openai_key: ipywidgets.Password = "1234556",
    )  -> str:      
    return "This is a dummy function. It returns nothing. "