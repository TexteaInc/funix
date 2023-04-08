import atexit
import importlib
import os
import sys
import socket
import typing
import urllib.parse
from threading import Thread
import webbrowser

import git

import funix.decorator as decorator
from funix.app import app
from funix.frontend import start

import inspect

import tempfile
import shutil
from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network

funix = decorator.funix
funix_yaml = decorator.funix_yaml
funix_json5 = decorator.funix_json5
import_theme = decorator.import_theme

set_default_theme = decorator.set_default_theme
clear_default_theme = decorator.clear_default_theme
set_theme = decorator.set_theme
set_theme_yaml = decorator.set_theme_yaml
set_theme_json5 = decorator.set_theme_json5

new_funix_type = decorator.new_funix_type


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
    now_port = port
    is_v4 = host.version == 4
    if is_this_host_on_this_network(host):
        new_host = "127.0.0.1" if is_v4 else "[::1]"
    else:
        new_host = host.compressed
    while check_port_is_used(now_port, new_host):
        if now_port > 65535 or now_port < 0:
            raise Exception("No available port!")
        now_port += 1
    return now_port


class OpenFrontend(Thread):
    def __init__(self, host: IPv4Address | IPv6Address, port: int):
        super(OpenFrontend, self).__init__()
        self.is_v4 = host.version == 4
        if is_this_host_on_this_network(host):
            self.host = "127.0.0.1" if self.is_v4 else "[::1]"
        else:
            self.host = host.compressed
        self.port = port

    def is_server_online(self) -> bool:
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            return True
        except:
            return False

    def run(self) -> None:
        while not self.is_server_online():
            pass
        webbrowser.open(f"http://{self.host}:{self.port}")


def __prep(main_class: typing.Optional[str], lazy: bool, need_path: bool):
    decorator.enable_wrapper()
    if main_class:
        module = importlib.import_module(main_class)
        if lazy:
            members = reversed(dir(module))
            for member in members:
                if inspect.isfunction(getattr(module, member)):
                    if need_path:
                        funix(__full_module=f"{module.__name__}")(getattr(module, member))
                    else:
                        funix()(getattr(module, member))
    else:
        print("Error: No Python module provided. \n How to fix: Please provide a module and try again. If your "
              "functions are in a file called hello.py, you should pass hello here. \n Example: funix hello")
        sys.exit(1)


def get_path_modules(path: str):
    sys.path.append(path)
    files = os.listdir(path)
    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            yield from get_path_modules(os.path.join(path, file))
        if file.endswith(".py"):
            if file == "__init__.py":
                continue
            yield file[:-3]


def run(
    main_class: str,
    host: typing.Optional[str] = "0.0.0.0",
    port: typing.Optional[int] = 3000,
    no_frontend: typing.Optional[bool] = False,
    no_browser: typing.Optional[bool] = False,
    lazy: typing.Optional[bool] = False,
    dir_mode: typing.Optional[bool] = False,
    package_mode: typing.Optional[bool] = False,
    from_git: typing.Optional[str] = None,
    repo_dir: typing.Optional[str] = None
):
    if from_git:
        tempdir = tempfile.mkdtemp()
        git.Repo.clone_from(url=from_git, to_path=tempdir)

        @atexit.register
        def clean_tempdir():
            shutil.rmtree(tempdir)

        new_path = tempdir
        if repo_dir:
            new_path = os.path.join(tempdir, repo_dir)
        sys.path.append(new_path)

        if main_class:
            pass
        elif dir_mode:
            main_class = new_path
        elif package_mode:
            raise Exception("Package mode is not supported for git mode, try to use dir mode!")
    if dir_mode:
        if os.path.exists(main_class) and os.path.isdir(main_class):
            for module in get_path_modules(main_class):
                __prep(main_class=module, lazy=lazy, need_path=True)
        else:
            raise Exception("Directory not found!")
    elif package_mode:
        module = importlib.import_module(main_class)
        path = module.__file__
        if path is None:
            raise Exception("`__init__.py` not found, please check this package!")
        for module in get_path_modules(os.path.dirname(path)):
            __prep(main_class=module, lazy=lazy, need_path=True)
    else:
        __prep(main_class=main_class, lazy=lazy, need_path=False)

    parsed_ip = ip_address(host)
    parsed_port = get_unused_port_from(port, parsed_ip)

    funix_secrets = decorator.export_secrets()
    if funix_secrets:
        is_v4 = parsed_ip.version == 4
        if is_this_host_on_this_network(parsed_ip):
            local = "127.0.0.1" if is_v4 else "[::1]"
        else:
            local = parsed_ip.compressed
        print("Secrets:")
        for name, secret in funix_secrets.items():
            if no_frontend:
                print(f"{name}\t{secret}")
            else:
                print(f"{name}\t{secret}\tLink: http://{local}:{port}/{urllib.parse.quote(name)}?secret={secret}")

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
