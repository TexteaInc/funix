"""
Reactive
"""
from inspect import Parameter, signature
from types import MappingProxyType
from typing import Callable

from flask import request

from funix.hint import ReactiveType

ReturnType = dict[str, tuple[Callable, dict[str, str]]]


def get_reactive_config(
    reactive: ReactiveType,
    function_params: MappingProxyType[str, Parameter],
    function_name: str,
) -> ReturnType:
    reactive_config: ReturnType = {}
    for reactive_param in reactive.keys():
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
                    if key not in function_params:
                        raise ValueError(
                            f"The key {key} is not in function, please write full config"
                        )
                    reactive_config[reactive_param][1][key] = key
    return reactive_config


def function_reactive_update(reactive_config: ReturnType) -> dict:
    reactive_param_value = {}

    form_data = request.get_json()

    for key_, item_ in reactive_config.items():
        argument_key: str = key_
        callable_function: Callable = item_[0]
        callable_config: dict[str, str] = item_[1]

        try:
            if callable_config == {}:
                reactive_param_value[argument_key] = callable_function(**form_data)
            else:
                new_form_data = {}
                for key__, value in callable_config.items():
                    new_form_data[key__] = form_data[value]
                reactive_param_value[argument_key] = callable_function(**new_form_data)
        except:
            pass

    if reactive_param_value == {}:
        return {"result": None}

    return {"result": reactive_param_value}
