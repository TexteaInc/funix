import importlib
import typing
from threading import Thread
import webbrowser

import funix.decorator as decorator
from funix.app import app
from funix.frontend import start

funix = decorator.funix
funix_yaml = decorator.funix_yaml
funix_json = decorator.funix_json

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
    print("Backend server running on http://{}:{}".format(host, port))
    if not no_frontend:
        print("Frontend server running on http://{}:{}".format(host, front_port))
        if not no_browser:
            webbrowser.open("http://{}:{}".format(host, front_port))
        frontend_start = Thread(target=start, kwargs={"host": host, "port": front_port, "backend_port": port})
        frontend_start.daemon = True
        frontend_start.start()
    app.run(host=host, port=port)
