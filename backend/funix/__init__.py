import sys
from importlib import import_module
from inspect import isfunction
from ipaddress import ip_address
from os import chdir, getcwd, listdir
from os.path import abspath, dirname, exists, isdir, join, normpath, sep
from sys import exit, path
from typing import Any, Generator, Optional
from urllib.parse import quote

from flask import Flask
from gitignore_parser import parse_gitignore

import funix.decorator as decorator
import funix.hint as hint
from funix.app import app, enable_funix_host_checker
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
funix_class = decorator.funix_class
funix_method = decorator.funix_method
# ---- Decorators ----

Limiter = decorator.Limiter

# ---- Theme ----
set_default_theme = decorator.set_default_theme
clear_default_theme = decorator.clear_default_theme
import_theme = decorator.import_theme
# ---- Theme ----

# ---- Util ----
new_funix_type_with_config_func = hint.new_funix_type_with_config_func
new_funix_type = hint.new_funix_type
set_app_secret = decorator.set_app_secret
# ---- Util ----
# ---- Exports ----

__use_git = False
"""
Funix uses git to clone repo, now this feature is optional.
"""

__now_path = getcwd()
"""
The current path. For switching the path.
"""

try:
    from git import Repo

    __use_git = True
except:
    pass


def get_path_difference(base_dir: str, target_dir: str) -> str | None:
    base_components = normpath(base_dir).split(sep)
    target_components = normpath(target_dir).split(sep)

    if not target_dir.startswith(base_dir):
        raise ValueError("The base directory is not a prefix of the target directory.")

    path_diff = target_components

    for _ in range(len(base_components)):
        path_diff.pop(0)

    return ".".join(path_diff)


def __prep(
    module_or_file: Optional[str],
    lazy: bool,
    need_path: bool,
    is_module: bool,
    need_name: bool,
    base_dir: Optional[str] = None,
    default: Optional[str] = None,
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
        base_dir (str): The base director, only for dir mode.
        default (str): Default function name
    """
    decorator.enable_wrapper()
    path_difference: str | None = None
    if base_dir:
        # dir mode
        module = module_or_file.split(sep)
        module[-1] = module[-1][:-3]  # remove .py
        module = sep.join(module)
        path_difference = get_path_difference(base_dir, module)
    if module_or_file:
        if is_module:
            if default:
                decorator.set_default_function_name(default)
            module = import_module(module_or_file)
        else:
            folder = sep.join(module_or_file.split(sep)[0:-1])
            if folder:
                chdir(folder)
            if base_dir and not lazy:
                decorator.set_now_module(path_difference)
                if default:
                    python_file, function_name = default.strip().split(":")
                    if abspath(join(__now_path, module_or_file)) == abspath(
                        join(__now_path, base_dir, python_file)
                    ):
                        decorator.set_dir_mode_default_info((True, function_name))
                    else:
                        decorator.set_dir_mode_default_info((False, None))
            module = import_module_from_file(
                join(__now_path, module_or_file), need_name
            )
            if base_dir and not lazy:
                decorator.clear_now_module()
            chdir(__now_path)
        if lazy:
            members = reversed(dir(module))
            for member in members:
                if isfunction(getattr(module, member)):
                    if member.startswith("__") or member.startswith("_FUNIX_"):
                        continue
                    if need_path:
                        if base_dir:
                            funix(menu=path_difference)(getattr(module, member))
                        else:
                            funix(menu=f"{module.__name__}")(getattr(module, member))
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
    base_dir: str,
    add_to_sys_path: bool,
    need_full_path: bool,
    is_dir: bool,
    matches: Any,
) -> Generator[str, None, None]:
    """
    Get all the Python files in a directory.

    Parameters:
        base_dir (str): The path.
        add_to_sys_path (bool): If the path should be added to sys.path.
        need_full_path (bool): If the full path is needed.
        is_dir (bool): If mode is dir mode.
        matches (Any): The matches.

    Returns:
        Generator[str, None, None]: The Python files.
    """
    if add_to_sys_path:
        path.append(base_dir)
    files = listdir(base_dir)
    for file in files:
        if isdir(join(base_dir, file)):
            yield from get_python_files_in_dir(
                join(base_dir, file), add_to_sys_path, need_full_path, is_dir, matches
            )
        if file.endswith(".py") and file != "__init__.py":
            full_path = join(base_dir, file)
            if matches:
                if matches(abspath(full_path)):
                    continue
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
    default: Optional[str] = None,
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
        default (str): Default function name, default is None

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
            chdir(abspath(new_path))

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
        base_dir = file_or_module_name
        if default and ":" not in default:
            raise ValueError(
                "Default function name should be in the format of `file:func` in dir mode!"
            )
        ignore_file = join(base_dir, ".funixignore")
        matches = None
        if exists(ignore_file):
            matches = parse_gitignore(abspath(ignore_file), base_dir=abspath(base_dir))
        for single_file in get_python_files_in_dir(
            base_dir=base_dir,
            add_to_sys_path=False,
            need_full_path=True,
            is_dir=True,
            matches=matches,
        ):
            __prep(
                module_or_file=single_file,
                lazy=lazy,
                need_path=True,
                is_module=False,
                need_name=True,
                base_dir=base_dir,
                default=default,
            )
    elif package_mode:
        if default or transform:
            print(
                "WARNING: Default mode and transform mode is not supported for package mode!"
            )
        module = import_module(file_or_module_name)
        module_path = module.__file__
        if module_path is None:
            raise RuntimeError(
                f"`__init__.py`  is not found inside module path: {module_path}!"
            )
        for module in get_python_files_in_dir(
            base_dir=dirname(module_path),
            add_to_sys_path=True,
            need_full_path=False,
            is_dir=False,
            matches=None,
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
        elif not file_or_module_name.endswith(".py"):
            raise RuntimeError(
                "This is not a Python file! You should change the file extension to `.py`."
            )
        else:
            if default and ":" in default:
                raise ValueError(
                    "Default function name should be in the format of `func` in file mode!"
                )
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
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
    global_rate_limit: decorator.Limiter | list | dict = [],
    ip_headers: Optional[list[str]] = None,
    __kumo_callback_url: Optional[str] = None,
    __kumo_callback_token: Optional[str] = None,
    __host_regex: Optional[str] = None,
) -> Flask:
    """
    Get flask application for the funix app.

    Parameters:
        file_or_module_name (str): The file or module name to run.
        no_frontend (bool): If you want to disable the frontend, default is False
        lazy (bool): If you want to enable lazy mode, default is False
        package_mode (bool): If you want to enable package mode, default is False
        from_git (str): If you want to run the app from a git repo, default is None
        repo_dir (str): If you want to run the app from a git repo, you can specify the directory, default is None
        transform (bool): If you want to enable transform mode, default is False
        app_secret (str | bool): If you want to set an app secret, default is False
        global_rate_limit (decorator.Limiter | list | dict): If you want to rate limit all API endpoints,
            default is an empty list
        ip_headers (list[str] | None): IP headers for extraction instead of peer IP, useful for applications
            behind reverse proxies
        __kumo_callback_url (str): The Kumo callback url, default is None, do not set it if you don't know what it is.
        __kumo_callback_token (str): The Kumo callback token, default is None, do not set it if you don't know what
                                     it is.
        __host_regex (str): The host checker regex, default is None.

    Returns:
        flask.Flask: The flask application.
    """
    decorator.set_kumo_info(__kumo_callback_url, __kumo_callback_token)
    decorator.set_rate_limiters(
        decorator.parse_limiter_args(global_rate_limit, "global_rate_limit")
    )
    decorator.set_ip_header(ip_headers)
    if __host_regex:
        enable_funix_host_checker(__host_regex)

    dir_mode = exists(file_or_module_name) and isdir(file_or_module_name)

    if dir_mode and package_mode:
        print(
            'Error: Cannot use both directory mode and package mode.\nPlease run "funix --help" for more information.'
        )
        sys.exit(1)

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
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    dev: Optional[bool] = False,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
    default: Optional[str] = None,
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
        package_mode (bool): If you want to enable package mode, default is False
        from_git (str): If you want to run the app from a git repo, default is None
        repo_dir (str): If you want to run the app from a git repo, you can specify the directory, default is None
        dev (bool): If you want to enable development mode, default is True
        transform (bool): If you want to enable transform mode, default is False
        app_secret (str | bool): If you want to set an app secret, default is False
        default (str): Default function name, default is None

    Returns:
        None
    """
    dir_mode = exists(file_or_module_name) and isdir(file_or_module_name)

    if dir_mode and package_mode:
        print(
            'Error: Cannot use both directory mode and package mode.\nPlease run "funix --help" for more information.'
        )
        sys.exit(1)

    import_from_config(
        file_or_module_name=file_or_module_name,
        lazy=lazy,
        dir_mode=dir_mode,
        package_mode=package_mode,
        from_git=from_git,
        repo_dir=repo_dir,
        transform=transform,
        app_secret=app_secret,
        default=default,
    )

    if decorator.is_empty_function_list():
        print(
            "No functions nor classes decorated by Funix. Could you wanna enable the lazy mode (add -l flag)?"
        )
        sys.exit(1)

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
    app.run(host=host, port=parsed_port, debug=dev)
