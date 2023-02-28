import argparse
import sys
import os
import socket

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Funix')
    parser.add_argument('this_class', type=str, help='this class', action='store')
    parser.add_argument('main_class', type=str, help='main class to import', action='store', default='functions')
    parser.add_argument('--host', '-H', help='host of frontend & backend', action='store', default='127.0.0.1')
    parser.add_argument('--port', '-p', help='port of frontend & backend', action='store', default='3000')
    parser.add_argument('--no-frontend', '-F', help='disable frontend', action='store_true', default=False)
    parser.add_argument('--no-browser', '-B', help='disable auto open browser', action='store_true', default=False)
    parsed_sys_args = parser.parse_args(sys.argv)
    no_frontend: bool = parsed_sys_args.no_frontend
    no_browser: bool = parsed_sys_args.no_browser
    host: str = os.getenv("HOST", parsed_sys_args.host)
    port: int = get_unused_port_from(int(os.getenv("PORT", parsed_sys_args.port)), host)
    run(
        host=host,
        port=port,
        main_class=parsed_sys_args.main_class,
        no_frontend=no_frontend,
        no_browser=no_browser
    )
