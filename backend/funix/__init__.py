import importlib
import typing

import funix.decorator as decorator
from funix.app import app


def __prep(main_class: typing.Optional[str] = "functions"):
    decorator.enable_wrapper()
    importlib.import_module(main_class)


def run(host: typing.Optional[str] = "localhost", port: typing.Optional[int] = 4010,
        main_class: typing.Optional[str] = "functions"):
    __prep(main_class=main_class)
    app.run(host, port)
