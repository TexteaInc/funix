import random, os, typing
import funix

@funix.funix(
    title="Per-argument configuration",
    description="""This example shows off per-argument customizations where configurations are aggregated by the name of arguments in the `argument_config` parameter.
    """,
    argument_config={
        "x": {
            "widget": "textarea", 
            "label": "a text area string"}, 
        "y": {
            "widget": "password", 
            "label": "a password string"}, 
    },
    show_source=True,
)
def per_argument(x: str, y:str):
    pass