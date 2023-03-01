import os
import plac
import socket
import sys

from . import *

def check_port_is_used(port: int, host: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        return True
    except:
        return False


def get_unused_port_from(port: int, host: str):
    print(f"Checking port {port} is used or not...")
    nowPort = port
    while check_port_is_used(nowPort, host):
        if nowPort == 65535:
            raise Exception("No port available!")
        nowPort += 1
    return nowPort

@plac.pos("main_class", "Main class to import")
@plac.opt("host", "Host of frontend and backend", abbrev = "H")
@plac.opt("port", "Port of frontend and backend", abbrev = "p")
@plac.flg("no_frontend", "Disable frontend server", abbrev = "F")
@plac.flg("no_browser", "Disable auto open browser", abbrev = "B")
def main(main_class = "functions", host = "127.0.0.1", port = 3000, no_frontend = False, no_browser = False):
    """Funix: Building web apps without manually creating widgets"""
    sys.path.append(os.getcwd())
    parsed_host: str = os.getenv("FUNIX_HOST", host)
    parsed_port: int = get_unused_port_from(int(os.getenv("FUNIX_PORT", port)), parsed_host)
    parsed_no_frontend: bool = os.getenv("FUNIX_NO_FRONTEND", no_frontend)
    parsed_no_browser: bool = os.getenv("FUNIX_NO_BROWSER", no_browser)
    run(
        host=parsed_host,
        port=parsed_port,
        main_class=main_class,
        no_frontend=parsed_no_frontend,
        no_browser=parsed_no_browser
    )

def cli_main():
    plac.call(main)

if __name__ == '__main__':
    cli_main()
