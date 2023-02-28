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
set_global_theme = decorator.set_global_theme

class OpenFrontend(Thread):
    def __init__(self, host: str, port: int):
        super(OpenFrontend, self).__init__()
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
        importlib.import_module("functions")

def run(
    host: typing.Optional[str] = "localhost",
    port: typing.Optional[int] = 3000,
    main_class: typing.Optional[str] = "functions",
    no_frontend: typing.Optional[bool] = False,
    no_browser: typing.Optional[bool] = False
):
    __prep(main_class=main_class)
    if host is None:
        host = "localhost"
    if port is None:
        port = 3000
    if main_class is None:
        main_class = "functions"
    if no_frontend is None:
        no_frontend = False
    if no_browser is None:
        no_browser = False
    if not no_frontend:
        print(f"Backend and frontend server running on http://{host}:{port}")
    else:
        print(f"Backend server running on http://{host}:{port}")
    if not no_frontend and not no_browser:
        start(host, port)
        if not no_browser:
            web_browser_start = OpenFrontend(host=host, port=port)
            web_browser_start.daemon = True
            web_browser_start.start()
    app.run(host=host, port=port)
