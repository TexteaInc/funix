from ipaddress import ip_address
from random import randint
from threading import Thread

from flask import Flask

from funix.app import GlobalSwitchOption
from funix.decorator.file import enable_file_service
from funix.decorator.lists import enable_list
from funix.util.network import get_unused_port_from, is_port_used


def jupyter(app: Flask) -> None:
    if GlobalSwitchOption.in_notebook:
        import logging

        logging.getLogger("werkzeug").setLevel(logging.ERROR)
    enable_file_service(app)
    enable_list(app)
    from IPython.display import IFrame, display

    port = get_unused_port_from(randint(3000, 4000), ip_address("127.0.0.1"))
    Thread(
        target=lambda: app.run(
            host="127.0.0.1", port=port, debug=True, use_reloader=False
        )
    ).start()
    while not is_port_used(port, "127.0.0.1"):
        pass
    GlobalSwitchOption.NOTEBOOK_PORT = port
    display(IFrame(f"http://127.0.0.1:{port}", width="100%", height=800))
