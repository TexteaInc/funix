from inspect import isclass
from typing import Any
from datetime import datetime

from pydantic import BaseModel


def response_item_to_class(response_item: Any, clazz: type) -> Any:
    """
    Convert a response item to a class instance.

    Parameters:
        response_item (Any): The response item to convert.
        clazz (type): The class to convert the response item to.

    Returns:
        Any: An instance of the class with the response item data.
    """
    if clazz is datetime:
        return datetime.fromisoformat(response_item)
    if isclass(clazz) and issubclass(clazz, BaseModel):
        return clazz.model_validate(response_item)
    try:
        return clazz(response_item)
    except Exception as e:
        return response_item
