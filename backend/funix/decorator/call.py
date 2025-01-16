import sys
from copy import deepcopy
from functools import wraps
from inspect import isgeneratorfunction
from json import dumps, loads
from traceback import format_exc
from typing import Any, Callable
from urllib.request import urlopen
from uuid import uuid4

from flask import request, session
from requests import post

from funix.app.websocket import StdoutToWebsocket
from funix.config import supported_upload_widgets
from funix.decorator.limit import Limiter, global_rate_limiters
from funix.decorator.magic import anal_function_result
from funix.decorator.param import get_dataframe_parse_metadata, get_parse_type_metadata
from funix.decorator.pre_fill import get_pre_fill_metadata
from funix.decorator.secret import get_secret_by_id
from funix.hint import PreFillEmpty, WrapperException
from funix.session import set_global_variable

kumo_callback_url: str | None = None
"""
Kumo callback url. For kumo only, only record the call numbers.
"""

kumo_callback_token: str | None = None
"""
Kumo callback token.
"""


def set_kumo_info(url: str, token: str) -> None:
    """
    Set the kumo info.

    Parameters:
        url (str): The url.
        token (str): The token.
    """
    global kumo_callback_url, kumo_callback_token
    kumo_callback_url = url
    kumo_callback_token = token


def kumo_callback():
    """
    Kumo callback.
    """
    global kumo_callback_url, kumo_callback_token
    if kumo_callback_url and kumo_callback_token:
        try:
            post(
                kumo_callback_url,
                json={
                    "token": kumo_callback_token,
                },
                timeout=1,
            )
        except:
            pass


def call_function_get_frame(func, *args, **kwargs):
    """
    From: https://stackoverflow.com/a/52358426
    Calls the function *func* with the specified arguments and keyword
    arguments and snatches its local frame before it actually executes.
    """

    frame = None
    trace = sys.gettrace()

    def snatch_locals(_frame, name, arg):
        nonlocal frame
        if frame is None and name == "call":
            frame = _frame
            sys.settrace(trace)
        return trace

    sys.settrace(snatch_locals)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(trace)
    return frame, result


def funix_call(
    app_name: str,
    limiters: list[Limiter] | None,
    need_websocket: bool,
    use_pandas: bool,
    pandas_module: Any,
    function_id: str,
    function: Callable,
    return_type_parsed: Any,
    cast_to_list_flag: bool,
    json_schema_props: dict,
    print_to_web: bool,
    secret_key: bool,
    ws=None,
):
    for limiter in global_rate_limiters + limiters:
        limit_result = limiter.rate_limit()
        if limit_result is not None:
            return limit_result

    try:
        if not session.get("__funix_id"):
            session["__funix_id"] = uuid4().hex
        if need_websocket:
            function_kwargs = loads(ws.receive())
        else:
            function_kwargs = request.get_json()
        kumo_callback()
        if use_pandas:
            if function_id in get_dataframe_parse_metadata():
                dataframe_metadata = get_dataframe_parse_metadata()[function_id]
                for need_argument in dataframe_metadata:
                    big_dict = {}
                    get_args = dataframe_metadata[need_argument]
                    for get_arg in get_args:
                        if get_arg in function_kwargs:
                            big_dict[get_arg] = deepcopy(function_kwargs[get_arg])
                            del function_kwargs[get_arg]
                    function_kwargs[need_argument] = pandas_module.DataFrame(big_dict)
        if function_id in get_parse_type_metadata():
            for func_arg, func_arg_type_class in get_parse_type_metadata()[
                function_id
            ].items():
                if func_arg in function_kwargs:
                    try:
                        function_kwargs[func_arg] = func_arg_type_class(
                            function_kwargs[func_arg]
                        )
                    except:
                        # Oh, my `typing`
                        continue

        def original_result_to_pre_fill_metadata(
            function_id_int: int,
            function_call_result: Any,
        ) -> None:
            """
            Document is on the way
            """
            function_call_address = str(function_id_int)
            if pre_fill_metadata := get_pre_fill_metadata(function_call_address):
                for index_or_key in pre_fill_metadata:
                    if index_or_key is PreFillEmpty:
                        set_global_variable(
                            app_name + function_call_address + "_result",
                            function_call_result,
                        )
                    else:
                        set_global_variable(
                            app_name + function_call_address + f"_{index_or_key}",
                            function_call_result[index_or_key],
                        )

        def pre_anal_result(frame: Any, function_call_result: Any):
            """
            Document is on the way
            """
            try:
                original_result_to_pre_fill_metadata(id(function), function_call_result)
                return anal_function_result(
                    frame,
                    app_name,
                    function_call_result,
                    return_type_parsed,
                    cast_to_list_flag,
                )
            except:
                return {
                    "error_type": "pre-anal",
                    "error_body": format_exc(),
                }

        @wraps(function)
        def wrapped_function(**wrapped_function_kwargs):
            """
            The function's wrapper
            """
            # TODO: Best result handling, refactor it if possible
            try:
                function_call_result = call_function_get_frame(
                    function, **wrapped_function_kwargs
                )
                return pre_anal_result(function_call_result[0], function_call_result[1])
            except WrapperException as e:
                return {
                    "error_type": "wrapper",
                    "error_body": str(e),
                }
            except:
                return {
                    "error_type": "function",
                    "error_body": format_exc(),
                }

        @wraps(function)
        def output_to_web_function(**wrapped_function_kwargs):
            try:
                fake_stdout = StdoutToWebsocket(ws)
                fake_stderr = StdoutToWebsocket(ws, is_err=True)
                org_stdout, sys.stdout = sys.stdout, fake_stdout
                org_stderr, sys.stderr = sys.stderr, fake_stderr
                if isgeneratorfunction(function):
                    for single_result in function(**wrapped_function_kwargs):
                        if single_result:
                            if isinstance(single_result, tuple):
                                for single_result_item in single_result:
                                    print(single_result_item)
                            else:
                                print(single_result)
                else:
                    function_result_ = function(**wrapped_function_kwargs)
                    if function_result_:
                        if isinstance(function_result_, tuple):
                            for single_result_item in function_result_:
                                print(single_result_item)
                        else:
                            print(function_result_)
                sys.stdout = org_stdout
                sys.stderr = org_stderr
            except:
                ws.send(
                    dumps(
                        {
                            "error_type": "function",
                            "error_body": format_exc(),
                        }
                    )
                )
            ws.close()

        cell_names = []
        upload_base64_files = {}

        # TODO: And the logic below, refactor it if possible

        for json_schema_prop_key in json_schema_props.keys():
            if "treat_as" in json_schema_props[json_schema_prop_key]:
                if json_schema_props[json_schema_prop_key]["treat_as"] == "cell":
                    cell_names.append(json_schema_prop_key)
            if "widget" in json_schema_props[json_schema_prop_key]:
                if (
                    json_schema_props[json_schema_prop_key]["widget"]
                    in supported_upload_widgets
                ):
                    upload_base64_files[json_schema_prop_key] = "single"
            if "items" in json_schema_props[json_schema_prop_key]:
                if "widget" in json_schema_props[json_schema_prop_key]["items"]:
                    if (
                        json_schema_props[json_schema_prop_key]["items"]["widget"]
                        in supported_upload_widgets
                    ):
                        upload_base64_files[json_schema_prop_key] = "multiple"

        if function_kwargs is None:
            empty_function_kwargs_error = {
                "error_type": "wrapper",
                "error_body": "No arguments passed to function.",
            }
            if need_websocket:
                ws.send(dumps(empty_function_kwargs_error))
                ws.close()
            else:
                return empty_function_kwargs_error
        if secret_key:
            if "__funix_secret" in function_kwargs:
                if (
                    not get_secret_by_id(app_name, function_id)
                    == function_kwargs["__funix_secret"]
                ):
                    incorrect_secret_error = {
                        "error_type": "wrapper",
                        "error_body": "Provided secret is incorrect.",
                    }
                    if need_websocket:
                        ws.send(dumps(incorrect_secret_error))
                        ws.close()
                    else:
                        return incorrect_secret_error
                else:
                    del function_kwargs["__funix_secret"]
            else:
                no_secret_error = {
                    "error_type": "wrapper",
                    "error_body": "No secret provided.",
                }
                if need_websocket:
                    ws.send(dumps(no_secret_error))
                    ws.close()
                else:
                    return no_secret_error

        if len(cell_names) > 0:
            length = len(function_kwargs[cell_names[0]])
            static_keys = function_kwargs.keys() - cell_names
            result = []
            for i in range(length):
                arg = {}
                for cell_name in cell_names:
                    arg[cell_name] = function_kwargs[cell_name][i]
                for static_key in static_keys:
                    arg[static_key] = function_kwargs[static_key]
                if need_websocket:
                    if print_to_web:
                        ws.send(
                            dumps(
                                {
                                    "error_type": "wrapper",
                                    "error_body": "Funix cannot handle cell, print_to_web and stream mode "
                                    "in the same time",
                                }
                            )
                        )
                        ws.close()
                        return
                    else:
                        result = []
                        for temp_function_result in function(**arg):
                            function_result = pre_anal_result(
                                None, temp_function_result
                            )
                            if isinstance(function_result, list):
                                result.extend(function_result)
                            else:
                                result.append(function_result)
                else:
                    temp_result = wrapped_function(**arg)
                    if isinstance(temp_result, list):
                        result.extend(temp_result)
                    else:
                        result.append(temp_result)
            if need_websocket:
                ws.send(dumps({"result": result}))
                ws.close()
                return
            else:
                return [{"result": result}]
        elif len(upload_base64_files) > 0:
            new_args = function_kwargs
            for upload_base64_file_key in upload_base64_files.keys():
                if upload_base64_file_key not in function_kwargs:
                    continue
                if not function_kwargs[upload_base64_file_key]:
                    continue
                if upload_base64_files[upload_base64_file_key] == "single":
                    with urlopen(function_kwargs[upload_base64_file_key]) as rsp:
                        new_args[upload_base64_file_key] = rsp.read()
                elif upload_base64_files[upload_base64_file_key] == "multiple":
                    for pos, each in enumerate(function_kwargs[upload_base64_file_key]):
                        with urlopen(each) as rsp:
                            new_args[upload_base64_file_key][pos] = rsp.read()
            if need_websocket:
                if print_to_web:
                    output_to_web_function(**new_args)
                else:
                    for temp_function_result in function(**new_args):
                        function_result = pre_anal_result(None, temp_function_result)
                        ws.send(dumps(function_result))
                    ws.close()
            else:
                return wrapped_function(**new_args)
        else:
            if need_websocket:
                if print_to_web:
                    output_to_web_function(**function_kwargs)
                else:
                    for temp_function_result in function(**function_kwargs):
                        function_result = pre_anal_result(None, temp_function_result)
                        ws.send(dumps(function_result))
                    ws.close()
            else:
                return wrapped_function(**function_kwargs)
    except:
        error = {"error_type": "wrapper", "error_body": format_exc()}
        if need_websocket:
            ws.send(dumps(error))
            ws.close()
        else:
            return error
