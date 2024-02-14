"""
URI utilities
"""
from typing import Optional
from urllib.parse import urlparse

from funix.config import banned_function_name_and_path


def is_valid_uri(uri: str) -> bool:
    """
    Check if a URI is valid.
    Your URI must have a scheme, a netloc, and a path.
    For example: `https://example.com/`.

    Parameters:
        uri (str): The URI.

    Returns:
        bool: If the URI is valid.
    """
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def get_endpoint(
    path: Optional[str], unique_function_name: Optional[str], function_name: str
) -> str:
    """
    Get the endpoint of a function.
    If the path is not provided, the unique function name or the function name will be used.
    If the path is provided, the path will be used.

    Parameters:
        path (str | None): The path.
        unique_function_name (str | None): The unique function name.
        function_name (str): The function name.

    Returns:
        str: The endpoint.

    Raises:
        Exception: If the path is not allowed.
    """
    if not path:
        if unique_function_name:
            return unique_function_name
        else:
            return function_name
    else:
        if path in banned_function_name_and_path:
            raise Exception(f"{function_name}'s path: {path} is not allowed")
        return path.strip("/")
