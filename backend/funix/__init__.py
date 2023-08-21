from importlib import import_module
from inspect import isfunction
from ipaddress import ip_address
from os import chdir, listdir
from os.path import dirname, exists, isdir, join
from sys import exit, path
from typing import Generator, Optional
from urllib.parse import quote

from flask import Flask

import funix.decorator as decorator
import funix.hint as hint
from funix.app import app
from funix.frontend import OpenFrontend, run_open_frontend, start
from funix.prep.global_to_session import get_new_python_file
from funix.util.file import create_safe_tempdir
from funix.util.module import import_module_from_file
from funix.util.network import (
    get_compressed_ip_address_as_str,
    get_unused_port_from,
    is_ip_on_localhost,
    is_port_used,
)

# ---- Exports ----
# ---- Decorators ----
funix = decorator.funix
# ---- Decorators ----

# ---- Theme ----
set_theme = decorator.set_theme
set_default_theme = decorator.set_default_theme
clear_default_theme = decorator.clear_default_theme
import_theme = decorator.import_theme
# ---- Theme ----

# ---- Util ----
new_funix_type = hint.new_funix_type
set_app_secret = decorator.set_app_secret
# ---- Util ----
# ---- Exports ----

__use_git = False
"""
Funix uses git to clone repo, now this feature is optional.
"""

try:
    from git import Repo

    __use_git = True
except:
    pass


def __prep(
    module_or_file: Optional[str],
    lazy: bool,
    need_path: bool,
    is_module: bool,
    need_name: bool,
) -> None:
    """
    Prepare the module or file. Import and wrap the functions if needed.
    Developers should not use this function. Import by yourself.

    Parameters:
        module_or_file (str): The module or file.
        lazy (bool): If the functions should be wrapped automatically.
        need_path (bool): If the path is needed.
        is_module (bool): Pass `True` if the module_or_file is a module, `False` if it is a file.
        need_name (bool): For the module, if the name is needed.
    """
    decorator.enable_wrapper()
    if module_or_file:
        if is_module:
            module = import_module(module_or_file)
        else:
            module = import_module_from_file(module_or_file, need_name)
        if lazy:
            members = reversed(dir(module))
            for member in members:
                if isfunction(getattr(module, member)):
                    if need_path:
                        funix(__full_module=f"{module.__name__}")(
                            getattr(module, member)
                        )
                    else:
                        funix()(getattr(module, member))
    else:
        print(
            "Error: No Python file, module or directory provided. "
            "\n How to fix: Please provide a file, module or directory and try again. If your "
            "functions are in a file called hello.py, you should pass hello.py here. \n Example: funix hello.py"
        )
        exit(1)


def get_python_files_in_dir(
    base_dir: str, add_to_sys_path: bool, need_full_path: bool
) -> Generator[str, None, None]:
    """
    Get all the Python files in a directory.

    Parameters:
        base_dir (str): The path.
        add_to_sys_path (bool): If the path should be added to sys.path.
        need_full_path (bool): If the full path is needed.

    Returns:
        Generator[str, None, None]: The Python files.
    """
    if add_to_sys_path:
        path.append(base_dir)
    files = listdir(base_dir)
    for file in files:
        if isdir(join(base_dir, file)):
            yield from get_python_files_in_dir(
                join(base_dir, file), add_to_sys_path, need_full_path
            )
        if file.endswith(".py") and file != "__init__.py":
            if need_full_path:
                yield join(base_dir, file)
            else:
                yield file[:-3]


def import_from_config(
    file_or_module_name: str,
    lazy: Optional[bool] = False,
    dir_mode: Optional[bool] = False,
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
) -> None:
    """
    Import files, git repos and modules from the config argument.

    Parameters:
        file_or_module_name (str): The file or module name to run.
        lazy (bool): If you want to enable lazy mode, default is False
        dir_mode (bool): If you want to enable dir mode, default is False
        package_mode (bool): If you want to enable package mode, default is False
        from_git (str): If you want to run the app from a git repo, default is None
        repo_dir (str): If you want to run the app from a git repo, you can specify the directory, default is None
        transform (bool): If you want to enable transform mode, default is False
        app_secret (str | bool): If you want to set an app secret, default is False

    Returns:
        None

    Raises:
        See code for more info.
    """
    if transform and (dir_mode or package_mode):
        raise ValueError("Transform mode is not supported for dir or package mode!")

    if __use_git:
        if from_git:
            tempdir = create_safe_tempdir()
            print("Please wait, cloning git repo...")
            Repo.clone_from(url=from_git, to_path=tempdir)
            new_path = tempdir
            if repo_dir:
                new_path = join(tempdir, repo_dir)
            path.append(new_path)
            chdir(new_path)

            if file_or_module_name:
                pass
            elif dir_mode:
                file_or_module_name = new_path
            elif package_mode:
                raise ValueError(
                    "Package mode is not supported for git mode, try to use dir mode!"
                )
    else:
        if from_git:
            raise Exception("GitPython is not installed, please install it first!")

    if app_secret and isinstance(app_secret, str):
        set_app_secret(app_secret)

    if dir_mode:
        if exists(file_or_module_name) and isdir(file_or_module_name):
            for single_file in get_python_files_in_dir(
                base_dir=file_or_module_name, add_to_sys_path=False, need_full_path=True
            ):
                __prep(
                    module_or_file=single_file,
                    lazy=lazy,
                    need_path=True,
                    is_module=False,
                    need_name=True,
                )
        else:
            raise RuntimeError(
                "Directory not found or not a directory! "
                "If you want to use package mode, please use --package/-P option, "
                "if you want to use file mode, please use remove --recursive/-R option."
            )
    elif package_mode:
        module = import_module(file_or_module_name)
        module_path = module.__file__
        if module_path is None:
            raise RuntimeError(
                f"`__init__.py`  is not found inside module path: {module_path}!"
            )
        for module in get_python_files_in_dir(
            base_dir=dirname(module_path), add_to_sys_path=True, need_full_path=False
        ):
            __prep(
                module_or_file=module,
                lazy=lazy,
                need_path=True,
                is_module=True,
                need_name=True,
            )
    else:
        if not exists(file_or_module_name):
            raise RuntimeError(
                "File not found! If you want to use package mode, please use --package/-P option"
            )
        elif isdir(file_or_module_name):
            raise RuntimeError(
                "Oh this is a directory! If you want to use directory/recursive mode, "
                "please use --recursive/-R option"
            )
        elif not file_or_module_name.endswith(".py"):
            raise RuntimeError(
                "This is not a Python file! You should change the file extension to `.py`."
            )
        else:
            if transform:
                __prep(
                    module_or_file=get_new_python_file(file_or_module_name),
                    lazy=lazy,
                    need_path=False,
                    is_module=False,
                    need_name=False,
                )
            else:
                __prep(
                    module_or_file=file_or_module_name,
                    lazy=lazy,
                    need_path=False,
                    is_module=False,
                    need_name=False,
                )


def get_flask_application(
    file_or_module_name: str,
    no_frontend: Optional[bool] = False,
    lazy: Optional[bool] = False,
    dir_mode: Optional[bool] = False,
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
) -> Flask:
    """
    Get flask application for the funix app.

    Parameters:
        file_or_module_name (str): The file or module name to run.
        no_frontend (bool): If you want to disable the frontend, default is False
        lazy (bool): If you want to enable lazy mode, default is False
        dir_mode (bool): If you want to enable dir mode, default is False
        package_mode (bool): If you want to enable package mode, default is False
        from_git (str): If you want to run the app from a git repo, default is None
        repo_dir (str): If you want to run the app from a git repo, you can specify the directory, default is None
        transform (bool): If you want to enable transform mode, default is False
        app_secret (str | bool): If you want to set an app secret, default is False

    Returns:
        flask.Flask: The flask application.
    """
    import_from_config(
        file_or_module_name=file_or_module_name,
        lazy=lazy,
        dir_mode=dir_mode,
        package_mode=package_mode,
        from_git=from_git,
        repo_dir=repo_dir,
        transform=transform,
        app_secret=app_secret,
    )

    if not no_frontend:
        start()
    return app


def run(
    file_or_module_name: str,
    host: Optional[str] = "0.0.0.0",
    port: Optional[int] = 3000,
    no_frontend: Optional[bool] = False,
    no_browser: Optional[bool] = False,
    lazy: Optional[bool] = False,
    dir_mode: Optional[bool] = False,
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    no_debug: Optional[bool] = False,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
) -> None:
    """
    Run the funix app.
    For more information, `funix -h` will help you.

    Parameters:
        file_or_module_name (str): The file or module name to run.
        host (str): The host to run the app on, default is "0.0.0.0"
        port (int): The port to run the app on, default is 3000
        no_frontend (bool): If you want to disable the frontend, default is False
        no_browser (bool): If you want to disable the browser opening, default is False
        lazy (bool): If you want to enable lazy mode, default is False
        dir_mode (bool): If you want to enable dir mode, default is False
        package_mode (bool): If you want to enable package mode, default is False
        from_git (str): If you want to run the app from a git repo, default is None
        repo_dir (str): If you want to run the app from a git repo, you can specify the directory, default is None
        no_debug (bool): If you want to disable debug mode, default is False
        transform (bool): If you want to enable transform mode, default is False
        app_secret (str | bool): If you want to set an app secret, default is False

    Returns:
        None
    """
    import_from_config(
        file_or_module_name=file_or_module_name,
        lazy=lazy,
        dir_mode=dir_mode,
        package_mode=package_mode,
        from_git=from_git,
        repo_dir=repo_dir,
        transform=transform,
        app_secret=app_secret,
    )

    parsed_ip = ip_address(host)
    parsed_port = get_unused_port_from(port, parsed_ip)

    funix_secrets = decorator.export_secrets()
    if funix_secrets:
        local = get_compressed_ip_address_as_str(parsed_ip)
        print("Secrets:")
        print("-" * 15)
        for name, secret in funix_secrets.items():
            print(f"Name: {name}")
            print(f"Secret: {secret}")
            if not no_frontend:
                print(f"Link: http://{local}:{port}/{quote(name)}?secret={secret}")
            print("-" * 15)

    if not no_frontend:
        start()
        print(f"Starting Funix at http://{host}:{parsed_port}")
    else:
        print(f"Starting Funix backend only at http://{host}:{parsed_port}")
    if not no_frontend and not no_browser:
        run_open_frontend(parsed_ip, parsed_port)
    app.run(host=host, port=parsed_port, debug=not no_debug)
