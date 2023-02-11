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
    def __init__(self, host: str, front_port: int, backend_port: int):
        super(OpenFrontend, self).__init__()
        self.host = host
        self.front_port = front_port
        self.backend_port = backend_port

    def isServerOnline(self) -> bool:
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.backend_port))
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.front_port))
            return True
        except:
            return False

    def run(self) -> None:
        while not self.isServerOnline():
            pass
        webbrowser.open(f"http://{self.host}:{self.front_port}")

def __prep(main_class: typing.Optional[str] = "functions"):
    decorator.enable_wrapper()
    importlib.import_module(main_class)

def run(
    host: typing.Optional[str] = "localhost",
    port: typing.Optional[int] = 8080,
    front_port: typing.Optional[int] = 80,
    main_class: typing.Optional[str] = "functions",
    no_frontend: typing.Optional[bool] = False,
    no_browser: typing.Optional[bool] = False
):
    __prep(main_class=main_class)
    print(f"Backend server running on http://{host}:{port}")
    if not no_frontend:
        print(f"Frontend server running on http://{host}:{front_port}")
        frontend_start = Thread(target=start, kwargs={"host": host, "port": front_port, "backend_port": port})
        frontend_start.daemon = True
        frontend_start.start()
        if not no_browser:
            web_browser_start = OpenFrontend(host=host, front_port=front_port, backend_port=port)
            web_browser_start.daemon = True
            web_browser_start.start()
    app.run(host=host, port=port)
