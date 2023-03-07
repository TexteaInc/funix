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

set_default_theme = decorator.set_default_theme
clear_default_theme = decorator.clear_default_theme
set_theme = decorator.set_theme
set_theme_yaml = decorator.set_theme_yaml
set_theme_json5 = decorator.set_theme_json5

from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network

def check_port_is_used(port: int, host: str):
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False

def is_this_host_on_this_network(ip: IPv4Address | IPv6Address):
    is_v4 = ip.version == 4
    if is_v4:
        return ip in ip_network("0.0.0.0/32")
    else:
        return ip in ip_network("::/128")

def get_unused_port_from(port: int, host: IPv4Address | IPv6Address):
    print(f"Checking port {port} is used or not...")
    nowPort = port
    is_v4 = host.version == 4
    if is_this_host_on_this_network(host):
        newHost = "127.0.0.1" if is_v4 else "::1"
    else:
        newHost = host.compressed
    while check_port_is_used(nowPort, newHost):
        if nowPort > 65535 or nowPort < 0:
            raise Exception("No available port!")
        nowPort += 1
    return nowPort

class OpenFrontend(Thread):
    def __init__(self, host: IPv4Address | IPv6Address, port: int):
        super(OpenFrontend, self).__init__()
        self.is_v4 = host.version == 4
        if is_this_host_on_this_network(host):
            self.host = "127.0.0.1" if self.is_v4 else "::1"
        else:
            self.host = host.compressed
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
    parsed_ip = ip_address(host)
    parsed_port = get_unused_port_from(port, parsed_ip)
    if not no_frontend:
        print(f"Starting Funix at http://{host}:{parsed_port}")
    else:
        print(f"Starting Funix backend only at http://{host}:{parsed_port}")
    if not no_frontend and not no_browser:
        start()
        if not no_browser:
            web_browser_start = OpenFrontend(host=parsed_ip, port=parsed_port)
            web_browser_start.daemon = True
            web_browser_start.start()
    app.run(host=host, port=parsed_port)
