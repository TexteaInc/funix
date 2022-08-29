import argparse
import sys

from . import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyDataFront')
    parser.add_argument('this_class', type=str, help='this class', action='store')
    parser.add_argument('main_class', type=str, help='main class to import', action='store', default='functions')
    parser.add_argument('--host', help='host of backend', action='store', default='localhost')
    parser.add_argument('--port', help='port of backend', action='store', default='4010')
    parsed_sys_args = parser.parse_args(sys.argv)
    run(host=parsed_sys_args.host, port=parsed_sys_args.port, main_class=parsed_sys_args.main_class)
