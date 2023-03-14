from ..widget import slider


def new_build_in_type(widget: str):
    def decorator(cls):
        cls.__funix__ = True
        cls.__funix_widget__ = widget
        cls.__funix_base__ = cls.__base__
        return cls

    return decorator


def set_config(func: callable):
    def cls_init(self, *args, **kwargs):
        self.__funix_has_config__ = True
        self.__funix_config__ = func(*args, **kwargs)[1]

    def decorator(cls):
        cls.__funix_need_config__ = True
        cls.__funix_has_config__ = False
        cls.__funix_config__ = None
        cls.__init__ = cls_init
        return cls

    return decorator


@new_build_in_type("inputbox")
class IntInputBox(int):
    pass


@new_build_in_type("slider")
@set_config(slider)
class IntSlider(int):
    pass


@new_build_in_type("inputbox")
class FloatInputBox(float):
    pass


@new_build_in_type("slider")
@set_config(slider)
class FloatSlider(float):
    pass


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

