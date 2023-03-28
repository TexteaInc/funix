import os
import plac
import sys
from . import *

@plac.pos("module_name", "The Python module containing functions to be turned into web apps by Funix. For example, if your functions are in the file hello.py, you should pass `hello` here.")
@plac.opt("host", "Host of Funix", abbrev = "H")
@plac.opt("port", "Port of Funix", abbrev = "p")
@plac.flg("no_frontend", "Disable frontend server", abbrev = "F")
@plac.flg("no_browser", "Disable auto open browser", abbrev = "B")
@plac.flg("lazy", "Load functions without decorator", abbrev = "l")
@plac.flg("dir_mode", "Enable directory mode", abbrev = "d")
def main(
    module_name = None,
    host = "0.0.0.0",
    port = 3000,
    no_frontend = False,
    no_browser = False,
    lazy = False,
    dir_mode = False
):
    """Funix: Building web apps without manually creating widgets

    Funix turns your Python function into a web app
    by building the UI from the function's signature,
    based on the mapping from variable types to UI widgets,
    customizable per-widget or kept consistent across apps via themes.

    Just write your core logic and leave the rest to Funix.
    Visit us at http://funix.io
    """

    if not module_name:
        print("Error: No Python module provided.\nPlease run \"funix --help\" for more information.")
        sys.exit(1)

    sys.path.append(os.getcwd())
    parsed_host: str = os.getenv("FUNIX_HOST", host)
    parsed_port: int = int(os.getenv("FUNIX_PORT", port))
    parsed_no_frontend: bool = os.getenv("FUNIX_NO_FRONTEND", no_frontend)
    parsed_no_browser: bool = os.getenv("FUNIX_NO_BROWSER", no_browser)
    parsed_lazy: bool = os.getenv("FUNIX_LAZY", lazy)
    parsed_dir_mode: bool = os.getenv("FUNIX_DIR_MODE", dir_mode)
    run(
        host=parsed_host,
        port=parsed_port,
        main_class=module_name,
        no_frontend=parsed_no_frontend,
        no_browser=parsed_no_browser,
        lazy=parsed_lazy,
        dir_mode=parsed_dir_mode
    )

def cli_main():
    plac.call(main, version="Funix 0.3.6")

if __name__ == '__main__':
    cli_main()
