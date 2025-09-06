"""
Reactive
"""

from inspect import Parameter, signature
from types import MappingProxyType
from typing import Callable

from flask import request

from funix.hint import ReactiveType
from funix.decorator.param import get_real_callable

ReturnType = dict[str, tuple[Callable, dict[str, str]]]


def get_reactive_config(
    reactive: ReactiveType,
    function_params: MappingProxyType[str, Parameter],
    function_name: str,
) -> ReturnType:
    reactive_config: ReturnType = {}
    for reactive_param in reactive.keys():
        if isinstance(reactive_param, tuple):
            for param in reactive_param:
                if param not in function_params:
                    raise ValueError(
                        f"Reactive param `{param}` not found in function `{function_name}`"
                    )
        else:
            if reactive_param not in function_params:
                raise ValueError(
                    f"Reactive param `{reactive_param}` not found in function `{function_name}`"
                )
        callable_or_with_config = reactive[reactive_param]

        if isinstance(callable_or_with_config, tuple):
            callable_ = callable_or_with_config[0]
            full_config = callable_or_with_config[1]
        else:
            callable_ = callable_or_with_config
            full_config = None

        callable_params = signature(callable_).parameters

        for callable_param in dict(callable_params.items()).values():
            if (
                callable_param.kind == Parameter.VAR_KEYWORD
                or callable_param.kind == Parameter.VAR_POSITIONAL
            ):
                reactive_config[reactive_param] = (callable_, {})
                break

        if reactive_param not in reactive_config:
            if full_config:
                reactive_config[reactive_param] = (callable_, full_config)
            else:
                reactive_config[reactive_param] = (callable_, {})
                for key in dict(callable_params.items()).keys():
                    if key in function_params:
                        reactive_config[reactive_param][1][key] = key
    return reactive_config


def function_reactive_update(
    reactive_config: ReturnType, app_name: str, qualname: str
) -> dict:
    reactive_param_value = {}
    cached_callable = {}

    form_data = request.get_json()

    def wrapped_callable(
        callable_function_: Callable, key: str, index: int, is_tuple: bool, **kwargs
    ):
        """
        A wrapper function to call the callable with the provided kwargs.
        """
        if id(callable_function_) in cached_callable:
            data = cached_callable[id(callable_function_)]
        else:
            data = callable_function_(**kwargs)
            cached_callable[id(callable_function_)] = data
        if is_tuple:
            if isinstance(data, tuple):
                return data[index]
            elif isinstance(data, list):
                return data[index]
            elif isinstance(data, dict):
                return data.get(key)
        else:
            return data

    index = 0
    for key_, item_ in reactive_config.items():
        argument_key: tuple = ()
        is_tuple = False
        if isinstance(key_, tuple):
            is_tuple = True
            argument_key = key_
        else:
            is_tuple = False
            argument_key = (key_,)
        for argument in argument_key:
            callable_function: Callable = get_real_callable(
                app_name, item_[0], qualname
            )
            callable_config: dict[str, str] = item_[1]

            try:
                if callable_config == {}:
                    reactive_param_value[argument] = wrapped_callable(
                        callable_function, argument, index, is_tuple, **form_data
                    )
                else:
                    new_form_data = {}
                    for key__, value in callable_config.items():
                        new_form_data[key__] = form_data[value]
                    reactive_param_value[argument] = wrapped_callable(
                        callable_function, argument, index, is_tuple, **new_form_data
                    )
            except Exception as e:
                print(f"Error in reactive function `{callable_function.__name__}`: {e}")
                pass
        index = index + 1

    if reactive_param_value == {}:
        return {"result": None}

    return {"result": reactive_param_value}
