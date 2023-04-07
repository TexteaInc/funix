import os
import plac
import sys
from . import run


@plac.pos("module_name",
          "The Python module containing functions to be turned into web apps by Funix. "
          "For example, if your functions are in the file hello.py, you should pass `hello` here.")
@plac.opt("host", "Host of Funix", abbrev="H")
@plac.opt("port", "Port of Funix", abbrev="p")
@plac.flg("no_frontend", "Disable frontend server", abbrev="F")
@plac.flg("no_browser", "Disable auto open browser", abbrev="B")
@plac.flg("lazy", "Load functions without decorator", abbrev="l")
@plac.flg("dir_mode", "Enable directory mode", abbrev="d")
@plac.flg("package_mode", "Enable package mode", abbrev="P")
@plac.opt("from_git", "Import module from git", abbrev="g")
@plac.opt("repo_dir", "The directories in the repo that need to be used", abbrev="r")
def main(
        module_name=None,
        host="0.0.0.0",
        port=3000,
        no_frontend=False,
        no_browser=False,
        lazy=False,
        dir_mode=False,
        package_mode=False,
        from_git=None,
        repo_dir=None,
):
    """Funix: Building web apps without manually creating widgets

    Funix turns your Python function into a web app
    by building the UI from the function's signature,
    based on the mapping from variable types to UI widgets,
    customizable per-widget or kept consistent across apps via themes.

    Just write your core logic and leave the rest to Funix.
    Visit us at http://funix.io
    """

    if not module_name and not from_git:
        print("Error: No Python module or git repo provided.\nPlease run \"funix --help\" for more information.")
        sys.exit(1)

    if dir_mode and package_mode:
        print(
            "Error: Cannot use both directory mode and package mode.\nPlease run \"funix --help\" for more information."
        )
        sys.exit(1)

    sys.path.append(os.getcwd())
    parsed_host: str = os.getenv("FUNIX_HOST", host)
    parsed_port: int = int(os.getenv("FUNIX_PORT", port))
    parsed_no_frontend: bool = os.getenv("FUNIX_NO_FRONTEND", no_frontend)
    parsed_no_browser: bool = os.getenv("FUNIX_NO_BROWSER", no_browser)
    parsed_lazy: bool = os.getenv("FUNIX_LAZY", lazy)
    parsed_dir_mode: bool = os.getenv("FUNIX_DIR_MODE", dir_mode)
    parsed_package_mode: bool = os.getenv("FUNIX_PACKAGE_MODE", package_mode)
    parsed_from_git: str = os.getenv("FUNIX_FROM_GIT", from_git)
    parsed_repo_dir: str = os.getenv("FUNIX_REPO_DIR", repo_dir)
    run(
        host=parsed_host,
        port=parsed_port,
        main_class=module_name,
        no_frontend=parsed_no_frontend,
        no_browser=parsed_no_browser,
        lazy=parsed_lazy,
        dir_mode=parsed_dir_mode,
        package_mode=parsed_package_mode,
        from_git=parsed_from_git,
        repo_dir=parsed_repo_dir
    )


def cli_main():
    plac.call(main, version="Funix 0.3.6")


if __name__ == '__main__':
    cli_main()
