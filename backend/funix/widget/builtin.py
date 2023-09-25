"""
This file contains all the built-in widget types.
"""

from typing import Any

from funix.widget import code, slider, textarea


def new_built_in_type(widget: str) -> callable:
    """
    Define a new built-in type.

    Parameters:
        widget(str): The name of the widget.

    Returns:
        The decorator.
    """

    def decorator(cls: Any) -> object:
        """
        Decorator for define a new built-in type.
        Will modify the class and add some attributes.
        Funix will know this is a funix-built-in type.

        Parameters:
            cls(Any): The class.

        Returns:
            The modified class.
        """
        cls.__funix__ = True
        cls.__funix_widget__ = widget
        cls.__funix_base__ = cls.__base__
        return cls

    return decorator


def attach_config(widget: callable, *args, **kwargs):
    """
    Attach the config generator to the class.
    For dynamic config generation.

    Parameters:
        widget(callable): The widget.
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        The decorator.
    """

    def decorator(cls: Any) -> object:
        """
        Decorator for put the config generator to the class.
        Will modify the class and add `__funix_config__` attribute.

        Parameters:
            cls(Any): The class.

        Returns:
            The modified class.
        """
        cls.__funix_config__ = widget(*args, **kwargs)[1]
        return cls

    return decorator


@new_built_in_type("inputbox")
class IntInputBox(int):
    """
    The built-in int type's input box.
    For input.

    Base Class: int
    """

    pass


def int_slider(*args, **kwargs) -> Any:
    """
    The built-in int type's slider.
    For input.

    Parameters:
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        class: The class.
    """

    @new_built_in_type("slider")
    @attach_config(slider, *args, **kwargs)
    class _IntSlider(int):
        """
        The built-in int type's slider class.

        Base Class: int
        """

        pass

    return _IntSlider


IntSlider = int_slider


@new_built_in_type("inputbox")
class FloatInputBox(float):
    """
    The built-in float type's input box.
    For input.

    Base Class: float
    """

    pass


def float_slider(*args, **kwargs):
    """
    The built-in float type's slider.
    For input.

    Parameters:
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        class: The class.
    """

    @new_built_in_type("slider")
    @attach_config(slider, *args, **kwargs)
    class _FloatSlider(float):
        """
        The built-in float type's slider class.

        Base Class: float
        """

        pass

    return _FloatSlider


FloatSlider = float_slider


@new_built_in_type("inputbox")
class StrInputBox(str):
    """
    The built-in str type's input box.
    For input.

    Base Class: str
    """

    pass


def str_textarea(*args, **kwargs) -> Any:
    """
    Tht built-in str type's textarea.
    For input.

    Parameters:
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        class: The class.
    """

    @new_built_in_type("textarea")
    @attach_config(textarea, *args, **kwargs)
    class _StrTextarea(str):
        """
        The built-in str type's textarea class.

        Base Class: str
        """

        pass

    return _StrTextarea


StrTextarea = str_textarea


@new_built_in_type("password")
class StrPassword(str):
    """
    The built-in str type's password.
    For input.

    Base Class: str
    """

    pass


@new_built_in_type("checkbox")
class BoolCheckBox(int):
    """
    The built-in bool type's checkbox.
    For input.

    Base Class: int
    """

    __funix_bool__ = True
    pass


@new_built_in_type("switch")
class BoolSwitch(int):
    """
    The built-in bool type's switch.
    For input.

    Base Class: int
    """

    __funix_bool__ = True
    pass


@new_built_in_type("image")
class BytesImage(bytes):
    """
    The built-in byte type's image.
    For input.

    Base Class: bytes
    """

    pass


@new_built_in_type("video")
class BytesVideo(bytes):
    """
    The built-in byte type's video.
    For input.

    Base Class: bytes
    """

    pass


@new_built_in_type("audio")
class BytesAudio(bytes):
    """
    The built-in bytes type's audio.
    For input.

    Base Class: bytes
    """

    pass


@new_built_in_type("file")
class BytesFile(bytes):
    """
    The built-in bytes type's file.
    For input.

    Base Class: bytes
    """

    pass


def str_code(*args, **kwargs) -> Any:
    """
    The built-in str type's code.
    For input.

    Parameters:
        *args: The args.
        **kwargs: The kwargs.

    Returns:
        class: The class.
    """

    @new_built_in_type("code")
    @attach_config(code, *args, **kwargs)
    class _StrCode(str):
        """
        The built-in str type's code class.

        Base Class: str
        """

        pass

    return _StrCode


StrCode = str_code
