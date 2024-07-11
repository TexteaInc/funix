from json import dumps

from flask import Response, request

__decorated_id_to_function_dict: dict[str, dict[str, str]] = {}
"""
A dict, key is function id, value is function name.
"""

__decorated_secret_functions_dict: dict[str, dict[str, str]] = {}
"""
A dict, key is function id, value is secret.
For checking if the secret is correct.
"""

__app_secret: dict[str, str | None] = {}
"""
App secret, for all functions.
"""


def get_secret_by_id(app_name: str, function_id: str) -> str | None:
    """
    Get the secret of a function by id.

    Parameters:
        app_name (str): The app name.
        function_id (str): The function id.

    Returns:
        str | None: The secret.
    """
    global __decorated_secret_functions_dict
    if app_name not in __decorated_secret_functions_dict:
        return None
    return __decorated_secret_functions_dict[app_name].get(function_id, None)


def set_function_secret(
    app_name: str, secret: str, function_id: str, function_name: str
) -> None:
    """
    Set the secret of a function.

    Parameters:
        app_name (str): The app name.
        secret (str): The secret.
        function_id (str): The function id.
        function_name (str): The function name (or with path).
    """
    global __decorated_secret_functions_dict, __decorated_id_to_function_dict
    if app_name not in __decorated_secret_functions_dict:
        __decorated_secret_functions_dict[app_name] = {
            function_id: secret,
        }
        __decorated_id_to_function_dict[app_name] = {
            function_id: function_name,
        }
    else:
        __decorated_secret_functions_dict[app_name][function_id] = secret
        __decorated_id_to_function_dict[app_name][function_id] = function_name


def set_app_secret(app_name: str, secret: str) -> None:
    """
    Set the app secret, it will be used for all functions.

    Parameters:
        app_name (str): The app name.
        secret (str): The secret.
    """
    global __app_secret
    __app_secret[app_name] = secret


def get_app_secret(app_name: str) -> str | None:
    """
    Get the app secret.

    Parameters:
        app_name (str): The app name.

    Returns:
        str | None: The app secret.
    """
    global __app_secret
    return __app_secret.get(app_name, None)


def export_secrets(app_name: str):
    """
    Export all secrets from the decorated functions.

    Parameters:
        app_name (str): The app name.
    """
    __new_dict: dict[str, str] = {}
    if app_name in __decorated_secret_functions_dict:
        for function_id, secret in __decorated_secret_functions_dict[app_name].items():
            __new_dict[__decorated_id_to_function_dict[app_name][function_id]] = secret
    return __new_dict


def check_secret(app_name: str, function_id: str):
    data = request.get_json()

    failed_data = Response(
        dumps(
            {
                "success": False,
            }
        ),
        mimetype="application/json",
        status=400,
    )

    if data is None:
        return failed_data

    if "secret" not in data:
        return failed_data

    user_secret = request.get_json()["secret"]
    if user_secret == __decorated_secret_functions_dict[app_name][function_id]:
        return Response(
            dumps(
                {
                    "success": True,
                }
            ),
            mimetype="application/json",
            status=200,
        )
    else:
        return failed_data
