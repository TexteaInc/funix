import importlib
import socket
import typing
from threading import Thread
import webbrowser

import funix.decorator as decorator
from funix.app import app
from funix.frontend import start

funix = decorator.funix
funix_yaml = decorator.funix_yaml
funix_json5 = decorator.funix_json5
import_theme = decorator.import_theme

set_default_theme = decorator.set_global_theme
clear_default_theme = decorator.clear_default_theme
set_theme = decorator.set_theme
set_theme_yaml = decorator.set_theme_yaml
set_theme_json5 = decorator.set_theme_json5

class OpenFrontend(Thread):
    def __init__(self, host: str, port: int):
        super(OpenFrontend, self).__init__()
        if host == "0.0.0.0" or host == "::":
            self.host = "localhost"
        else:
            self.host = host
        self.port = port

    def isServerOnline(self) -> bool:
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            return True
        except:
            return False

    def run(self) -> None:
        while not self.isServerOnline():
            pass
        webbrowser.open(f"http://{self.host}:{self.port}")

def __prep(main_class: typing.Optional[str]):
    decorator.enable_wrapper()
    if main_class:
        importlib.import_module(main_class)
    else:
        print ("Error: No Python module provided. \n How to fix: Please provide a module and try again. If your functions are in a file called hello.py, you should pass hello here. \n Example: funix hello")
        exit()

def run(
    main_class: str,
    host: typing.Optional[str] = "0.0.0.0",
    port: typing.Optional[int] = 3000,
    no_frontend: typing.Optional[bool] = False,
    no_browser: typing.Optional[bool] = False
):
    __prep(main_class=main_class)
    if not no_frontend:
        print(f"Starting Funix at http://{host}:{port}")
    else:
        print(f"Starting Funix backend only at http://{host}:{port}")
    if not no_frontend and not no_browser:
        start()
        if not no_browser:
            web_browser_start = OpenFrontend(host=host, port=port)
            web_browser_start.daemon = True
            web_browser_start.start()
    app.run(host=host, port=port)
