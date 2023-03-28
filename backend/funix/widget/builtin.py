from ..widget import slider, code


def new_build_in_type(widget: str):
    def decorator(cls):
        cls.__funix__ = True
        cls.__funix_widget__ = widget
        cls.__funix_base__ = cls.__base__
        return cls

    return decorator


def put_config(widget, *args, **kwargs):
    def decorator(cls):
        cls.__funix_config__ = widget(*args, **kwargs)[1]
        return cls
    return decorator


@new_build_in_type("inputbox")
class IntInputBox(int):
    pass


def int_slider(*args, **kwargs):
    @new_build_in_type("slider")
    @put_config(slider, *args, **kwargs)
    class _IntSlider(int):
        pass
    return _IntSlider


IntSlider = int_slider


@new_build_in_type("inputbox")
class FloatInputBox(float):
    pass


def float_slider(*args, **kwargs):
    @new_build_in_type("slider")
    @put_config(slider, *args, **kwargs)
    class _FloatSlider(float):
        pass
    return _FloatSlider


FloatSlider = float_slider


@new_build_in_type("inputbox")
class StrInputBox(str):
    pass


@new_build_in_type("textarea")
class StrTextarea(str):
    pass


@new_build_in_type("password")
class StrPassword(str):
    pass


@new_build_in_type("checkbox")
class BoolCheckBox(int):
    __funix_bool__ = True
    pass


@new_build_in_type("switch")
class BoolSwitch(int):
    __funix_bool__ = True
    pass


@new_build_in_type("image")
class BytesImage(bytes):
    pass


@new_build_in_type("video")
class BytesVideo(bytes):
    pass


@new_build_in_type("audio")
class BytesAudio(bytes):
    pass


@new_build_in_type("file")
class BytesFile(bytes):
    pass


def str_code(*args, **kwargs):
    @new_build_in_type("code")
    @put_config(code, *args, **kwargs)
    class _StrCode(str):
        pass
    return _StrCode


StrCode = str_code
