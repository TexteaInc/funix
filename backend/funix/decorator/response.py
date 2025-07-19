from typing import Any
from datetime import datetime


def response_item_to_class(response_item: Any, clazz: type) -> Any:
    """
    Convert a response item to a class instance.

    Parameters:
        response_item (Any): The response item to convert.
        clazz (type): The class to convert the response item to.

    Returns:
        Any: An instance of the class with the response item data.
    """
    try:
        if clazz is datetime:
            return datetime.fromisoformat(response_item)
        return clazz(response_item)
    except Exception as e:
        print(e)
        return response_item
