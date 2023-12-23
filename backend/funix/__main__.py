import os
import secrets
import sys

import plac

from funix import run


@plac.pos(
    "file_folder_or_module_name",
    "The Python module containing functions to be turned into web apps by Funix. "
    "For example, if your functions are in the file `hello.py`, you should pass `hello.py` here. "
    "if you want to turn a module called `hello` into a web app, you should pass `hello` here, "
    "and with --package or -P flag. "
    "if you want to turn a full folder called `examples` into a web app, you should pass `examples` here.",
)
@plac.opt("host", "Host of Funix", abbrev="H")
@plac.opt("port", "Port of Funix", abbrev="p")
@plac.flg("no_frontend", "Disable frontend server", abbrev="F")
@plac.flg("no_browser", "Disable auto open browser", abbrev="B")
@plac.flg("lazy", "Load functions without decorator", abbrev="l")
@plac.flg("package", "Enable package mode", abbrev="P")
@plac.flg("dev", "Enable development mode", abbrev="d")
@plac.flg("transform", "Transform the globals to a session variables", abbrev="t")
@plac.opt("from_git", "Import module from git", abbrev="g")
@plac.opt("repo_dir", "The directories in the repo that need to be used", abbrev="r")
@plac.opt("secret", "The secret key for the full app", abbrev="s")
@plac.opt("default", "The default function to run", abbrev="D")
def main(
    file_folder_or_module_name=None,
    host="0.0.0.0",
    port=3000,
    no_frontend=False,
    no_browser=False,
    lazy=False,
    package=False,
    dev=False,
    transform=False,
    from_git=None,
    repo_dir=None,
    secret=None,
    default=None,
):
    """Funix: Building web apps without manually creating widgets

    Funix turns your Python function into a web app
    by building the UI from the function's signature,
    based on the mapping from variable types to UI widgets,
    customizable per-widget or kept consistent across apps via themes.

    Just write your core logic and leave the rest to Funix.
    Visit us at http://funix.io"""

    if not file_folder_or_module_name and not from_git:
        print(
            'Error: No Python module, file or git repo provided.\nPlease run "funix --help" for more information.'
        )
        sys.exit(1)

    sys.path.append(os.getcwd())
    parsed_host: str = os.getenv("FUNIX_HOST", host)
    parsed_port: int = int(os.getenv("FUNIX_PORT", port))
    parsed_no_frontend: bool = os.getenv("FUNIX_NO_FRONTEND", no_frontend)
    parsed_no_browser: bool = os.getenv("FUNIX_NO_BROWSER", no_browser)
    parsed_lazy: bool = os.getenv("FUNIX_LAZY", lazy)
    parsed_package_mode: bool = os.getenv("FUNIX_PACKAGE_MODE", package)
    parsed_from_git: str = os.getenv("FUNIX_FROM_GIT", from_git)
    parsed_repo_dir: str = os.getenv("FUNIX_REPO_DIR", repo_dir)
    parsed_dev: bool = os.getenv("FUNIX_NO_DEV", dev)
    parsed_transform: bool = os.getenv("FUNIX_TRANSFORM", transform)
    parsed_secret: bool | str = os.getenv("FUNIX_SECRET", secret)
    parsed_default: str = os.getenv("FUNIX_DEFAULT", default)

    if isinstance(parsed_secret, str):
        if parsed_secret.lower() == "true":
            parsed_secret = True
        elif parsed_secret.lower() == "false" or parsed_secret == "":
            parsed_secret = False
    elif parsed_secret is None:
        parsed_secret = False

    if isinstance(parsed_secret, bool) and parsed_secret:
        parsed_secret = secrets.token_hex(16)

    run(
        host=parsed_host,
        port=parsed_port,
        file_or_module_name=file_folder_or_module_name,
        no_frontend=parsed_no_frontend,
        no_browser=parsed_no_browser,
        lazy=parsed_lazy,
        package_mode=parsed_package_mode,
        from_git=parsed_from_git,
        repo_dir=parsed_repo_dir,
        dev=parsed_dev,
        transform=parsed_transform,
        app_secret=parsed_secret,
        default=parsed_default,
    )


def cli_main():
    """
    The entry point for the command line interface.

    This function is called when you run `python -m funix` or `funix` from the command line.
    """
    plac.call(main, version="Funix 0.5.4")


if __name__ == "__main__":
    cli_main()
