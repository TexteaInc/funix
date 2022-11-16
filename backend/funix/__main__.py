import argparse
import sys
import os

from . import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Funix')
    parser.add_argument('this_class', type=str, help='this class', action='store')
    parser.add_argument('main_class', type=str, help='main class to import', action='store', default='functions')
    parser.add_argument('--host', help='host of backend', action='store', default='0.0.0.0')
    parser.add_argument('--port', help='port of backend', action='store', default='8080')
    parsed_sys_args = parser.parse_args(sys.argv)
    host: str = os.getenv("HOST", parsed_sys_args.host)
    port: int = int(os.getenv("PORT", parsed_sys_args.port))
    run(host=host, port=port, main_class=parsed_sys_args.main_class)
