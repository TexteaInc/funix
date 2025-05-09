import sys
from importlib import import_module
from ipaddress import ip_address
from os import chdir, getcwd
from os.path import abspath, dirname, exists, isdir, join, sep, splitext
from sys import exit, path
from typing import Optional
from urllib.parse import quote

from flask import Flask
from gitignore_parser import parse_gitignore

import funix.decorator as decorator
import funix.decorator.call as call
import funix.decorator.limit as limit
import funix.decorator.lists as lists
import funix.decorator.secret as secret
import funix.decorator.theme as theme
import funix.decorator.widget as widget
import funix.hint as hint
from funix.app import app, enable_funix_host_checker
from funix.config.switch import GlobalSwitchOption
from funix.frontend import run_open_frontend, start
from funix.jupyter import jupyter
from funix.prep.global_to_session import get_new_python_file
from funix.util.file import (
    create_safe_tempdir,
    get_path_difference,
    get_python_files_in_dir,
)
from funix.util.module import handle_module, import_module_from_file
from funix.util.network import (
    get_compressed_ip_address_as_str,
    get_unused_port_from,
    is_port_used,
)

# ---- Exports ----
# ---- Decorators ----
funix = decorator.funix
funix_class = decorator.funix_class
funix_method = decorator.funix_method
# ---- Decorators ----

Limiter = limit.Limiter

# ---- Theme ----
set_default_theme = theme.set_default_theme
clear_default_theme = theme.clear_default_theme
import_theme = theme.import_theme
# ---- Theme ----

# ---- Util ----
new_funix_type_with_config_func = hint.new_funix_type_with_config_func
new_funix_type = hint.new_funix_type
set_app_secret = secret.set_app_secret
generate_redirect_link = widget.generate_redirect_link
# ---- Util ----

# ---- Exports ----

__use_git = False
"""
Funix uses git to clone repo, now this feature is optional.
"""

now_path = getcwd()
"""
The current path. For switching the path.
"""

try:
    from git import Repo

    __use_git = True
except:
    pass


def enable_jupyter(value: bool):
    GlobalSwitchOption.NOTEBOOK_AUTO_EXECUTION = value


def __prep(
    module_or_file: Optional[str],
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
        module[-1] = splitext(module[-1])[0]
        module = sep.join(module)
        path_difference = get_path_difference(base_dir, module)
    if module_or_file:
        if is_module:
            if default:
                lists.set_default_function_name(app.name, default)
            module = import_module(module_or_file)
            handle_module(module, need_path, base_dir, path_difference)
        else:
            folder = sep.join(module_or_file.split(sep)[0:-1])
            if folder:
                chdir(folder)
            if base_dir:
                decorator.set_now_module(path_difference)
                if default:
                    python_file, function_name = default.strip().split(":")
                    if abspath(join(now_path, module_or_file)) == abspath(
                        join(now_path, base_dir, python_file)
                    ):
                        decorator.set_dir_mode_default_info((True, function_name))
                    else:
                        decorator.set_dir_mode_default_info((False, None))
            module = import_module_from_file(join(now_path, module_or_file), need_name)
            handle_module(module, need_path, base_dir, path_difference)
            if base_dir:
                decorator.clear_now_module()
            chdir(now_path)
    else:
        print(
            "Error: No Python file, module or directory provided. "
            "\n How to fix: Please provide a file, module or directory and try again. If your "
            "functions are in a file called hello.py, you should pass hello.py here. \n Example: funix hello.py"
        )
        exit(1)


def import_from_config(
    file_or_module_name: str,
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
    global now_path
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
            now_path = getcwd()

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
        set_app_secret(app.name, app_secret)

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
                    need_path=False,
                    is_module=False,
                    need_name=False,
                )
            else:
                __prep(
                    module_or_file=file_or_module_name,
                    need_path=False,
                    is_module=False,
                    need_name=False,
                )


def get_flask_application(
    file_or_module_name: str,
    no_frontend: Optional[bool] = False,
    package_mode: Optional[bool] = False,
    from_git: Optional[str] = None,
    repo_dir: Optional[str] = None,
    transform: Optional[bool] = False,
    app_secret: Optional[str | bool] = False,
    global_rate_limit: decorator.Limiter | list | dict = None,
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
    new_global_rate_limit = [] if global_rate_limit is None else global_rate_limit
    call.set_kumo_info(__kumo_callback_url, __kumo_callback_token)
    limit.set_rate_limiters(
        limit.parse_limiter_args(new_global_rate_limit, "global_rate_limit")
    )
    limit.set_ip_header(ip_headers)
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
        dir_mode=dir_mode,
        package_mode=package_mode,
        from_git=from_git,
        repo_dir=repo_dir,
        transform=transform,
        app_secret=app_secret,
    )

    if not no_frontend:
        start(app)
    return app


def run(
    file_or_module_name: str,
    host: Optional[str] = "0.0.0.0",
    port: Optional[int] = 3000,
    no_frontend: Optional[bool] = False,
    no_browser: Optional[bool] = False,
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
        dir_mode=dir_mode,
        package_mode=package_mode,
        from_git=from_git,
        repo_dir=repo_dir,
        transform=transform,
        app_secret=app_secret,
        default=default,
    )

    if lists.is_empty_function_list(app.name):
        print(
            "No functions nor classes decorated by Funix. Please check your code: "
            "functions and classes that need to be handled by Funix should be public "
            "and the objects should not be disable in `@funix.funix`."
        )
        sys.exit(1)

    parsed_ip = ip_address(host)
    parsed_port = get_unused_port_from(port, parsed_ip)

    funix_secrets = secret.export_secrets(app.name)
    if funix_secrets:
        local = get_compressed_ip_address_as_str(parsed_ip)
        print("Secrets:")
        print("-" * 15)
        for name, secret_ in funix_secrets.items():
            print(f"Name: {name}")
            print(f"Secret: {secret_}")
            if not no_frontend:
                print(
                    f"Link: http://{host}:{parsed_port}/{quote(name)}?secret={secret_}"
                )
            print("-" * 15)

    if not no_frontend:
        start(app)
        print(f"Starting Funix at http://{host}:{parsed_port}")
    else:
        print(f"Starting Funix backend only at http://{host}:{parsed_port}")
    if not no_frontend and not no_browser:
        run_open_frontend(parsed_ip, parsed_port)
    app.run(host=host, port=parsed_port, debug=dev)
