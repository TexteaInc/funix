"""
Generate and parse 
"""

import secrets
from typing import Union

false_words: list[str] = ["false", "no", "off", "0", "null", "none", "nil", ""]

true_words: list[str] = ["true", "yes", "on", "1"]


def get_secret_key_from_option(secret: Union[str, bool, None]) -> Union[str, bool]:
    """
    Get the secret key from the option, if it is true value, generate a new secret key.
    if it is false value, return false no whatever the value is.
    if it is a string, return the string.

    Parameters:
        secret (str | bool): The secret key.

    Returns:
        str | bool: The secret key.
    """
    if isinstance(secret, str):
        if secret.lower() in true_words:
            return secrets.token_hex(16)
        elif secret.lower() in false_words:
            return False
        else:
            return secret
    elif isinstance(secret, bool):
        return secrets.token_hex(16) if secret else False
    else:
        # None
        return False
