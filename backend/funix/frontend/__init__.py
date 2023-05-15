"""
Handle frontend requests and start the frontend.
"""

from ipaddress import IPv4Address, IPv6Address
from os.path import abspath, exists, join
from threading import Thread
from webbrowser import open

from flask import send_from_directory

from funix.app import app
from funix.util.network import get_compressed_ip_address_as_str, is_port_used

folder = abspath(join(abspath(__file__), "../../build"))  # Best abs path ever


class OpenFrontend(Thread):
    """
    Open the frontend in the browser.

    Base Class:
        threading.Thread: The thread.

    Attributes:
        host (IPv4Address | IPv6Address): The host.
        port (int): The port.
    """

    def __init__(self, host: IPv4Address | IPv6Address, port: int):
        """
        Create a new OpenFrontend instance.

        Parameters:
            host (IPv4Address | IPv6Address): The host.
            port (int): The port.

        Returns:
            OpenFrontend: The new OpenFrontend instance.
        """
        super(OpenFrontend, self).__init__()
        self.host = get_compressed_ip_address_as_str(host)
        self.port = port

    def is_server_online(self) -> bool:
        """
        Check if the server is online.

        Returns:
            bool: If the server is online.
        """
        return is_port_used(self.port, self.host)

    def run(self) -> None:
        """
        Open the frontend in the browser.
        """
        while not self.is_server_online():
            pass
        open(f"http://{self.host}:{self.port}")


def run_open_frontend(host: IPv4Address | IPv6Address, port: int) -> None:
    """
    Run the OpenFrontend thread.

    Parameters:
        host (IPv4Address | IPv6Address): The host.
        port (int): The port.
    """
    web_browser = OpenFrontend(host, port)
    web_browser.daemon = True  # Die when the main thread dies
    web_browser.start()


def start() -> None:
    """
    Start the frontend.
    """

    @app.route("/")
    def __send_index():
        """
        Send the index.html file.

        Routes:
            /: The index.html file.

        Returns:
            flask.Response: The index.html file.
        """
        return send_from_directory(folder, "index.html")

    @app.route("/<path:path>")
    def __send_root_files(path):
        """
        Send the static files in root or the index.html file for funix frontend.
        If the file doesn't exist, it will send the index.html file.

        Routes:
            /<path:path>: The static files or the index.html file.

        Parameters:
            path (str): The path to the file.

        Returns:
            flask.Response: The static files or the index.html file.
        """
        if exists(join(folder, path)):
            return send_from_directory(folder, path)
        return send_from_directory(folder, "index.html")

    @app.route("/static/<path:res>/<path:path>")
    def __send_static_files(res, path):
        """
        Send the static files.

        Routes:
            /static/<path:res>/<path:path>: The static files.

        Parameters:
            res (str): The resource folder.
            path (str): The path to the file.

        Returns:
            flask.Response: The static files.
        """
        return send_from_directory(abspath(join(folder, f"static/{res}/")), path)
