"""
URI utilities
"""

from urllib.parse import urlparse


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
