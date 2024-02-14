"""
Limiter
"""
import dataclasses
import time
from collections import deque
from json import dumps
from typing import Optional, Union

from flask import Response, request, session
from requests.structures import CaseInsensitiveDict

from funix.hint import LimitSource

ip_headers: list[str] = []
"""
IP headers for extraction, useful for applications behind reverse proxies

e.g. `X-Forwarded-For`, `X-Real-Ip` e.t.c
"""


@dataclasses.dataclass
class Limiter:
    call_history: dict
    # How many calls client can send between each interval set by `period`
    max_calls: int
    # Max call interval time, in seconds
    period: int
    source: LimitSource

    def __init__(
        self,
        max_calls: int = 10,
        period: int = 60,
        source: LimitSource = LimitSource.SESSION,
    ):
        if type(max_calls) is not int:
            raise TypeError("type of `max_calls` is not int")
        if type(period) is not int:
            raise TypeError("type of `period` is not int")
        if type(source) is not LimitSource:
            raise TypeError("type of `source` is not LimitSource")

        self.source = source
        self.max_calls = max_calls
        self.period = period
        self.call_history = {}

    @staticmethod
    def ip(max_calls: int, period: int = 60):
        return Limiter(max_calls=max_calls, period=period, source=LimitSource.IP)

    @staticmethod
    def session(max_calls: int, period: int = 60):
        return Limiter(max_calls=max_calls, period=period, source=LimitSource.SESSION)

    @staticmethod
    def dict_get_int(dictionary: dict | CaseInsensitiveDict, key: str) -> Optional[int]:
        if key not in dictionary:
            return None
        value = dictionary[key]
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        raise ValueError(
            f"The value of key `{key}` is `{value}`, cannot parse to integer"
        )

    @staticmethod
    def from_dict(dictionary: dict):
        converted = CaseInsensitiveDict(dictionary)
        ip = Limiter.dict_get_int(converted, "per_ip")
        session_ = Limiter.dict_get_int(converted, "per_browser")

        if ip is not None and session_ is not None:
            raise TypeError(
                "`per_ip` and `per_browser` are conflicting options in a single dict"
            )

        if ip is None and session_ is None:
            raise TypeError("`per_ip` or `per_browser` is required")

        max_calls = ip or session_
        source = LimitSource.IP
        if ip is not None:
            source = LimitSource.IP
        if session_ is not None:
            source = LimitSource.SESSION
        period = Limiter.dict_get_int(converted, "period") or 60

        return Limiter(max_calls=max_calls, period=period, source=source)

    def rate_limit(self) -> Optional[Response]:
        call_history = self.call_history
        match self.source:
            case LimitSource.IP:
                source: Optional[str] = None
                for header in ip_headers:
                    if header in request.headers:
                        source = request.headers[header]
                        break

                if source is None:
                    source = request.remote_addr

            case LimitSource.SESSION:
                source = session.get("__funix_id")

            case _:
                raise ValueError("Invalid source")

        if source not in call_history:
            call_history[source] = deque()

        queue = call_history[source]
        current_time = time.time()

        while len(queue) > 0 and current_time - queue[0] > self.period:
            queue.popleft()

        if len(queue) >= self.max_calls:
            time_passed = current_time - queue[0]
            time_to_wait = int(self.period - time_passed)
            error_message = {
                "error_body": f"Rate limit exceeded. Please try again in {time_to_wait} seconds.",
                "error_type": "safe_checker",
            }
            return Response(
                dumps(error_message), status=429, mimetype="application/json"
            )

        queue.append(current_time)
        return None


def set_ip_header(headers: Optional[list[str]]):
    global ip_headers
    if headers is None:
        return

    if len(headers) == 0:
        return

    ip_headers = headers


def parse_limiter_args(
    rate_limit: Union[Limiter, list, dict, None], arg_name: str = "rate_limit"
) -> Optional[list[Limiter]]:
    if rate_limit is None:
        return []
    if isinstance(rate_limit, Limiter):
        limiters = [rate_limit]
    elif isinstance(rate_limit, dict):
        converted = CaseInsensitiveDict(rate_limit)

        per_ip = Limiter.dict_get_int(converted, "per_ip")
        per_session = Limiter.dict_get_int(converted, "per_browser")
        limiters = []
        if per_ip:
            limiters.append(Limiter.ip(per_ip))
        if per_session:
            limiters.append(Limiter.ip(per_session))
        if len(limiters) == 0:
            raise TypeError(
                f"Dict passed for `{arg_name}` but no limiters are provided, something wrong."
            )

    elif isinstance(rate_limit, list):
        limiters = []
        for element in rate_limit:
            if isinstance(element, Limiter):
                limiters.append(element)
            elif isinstance(element, dict):
                limiters.append(Limiter.from_dict(element))
            else:
                raise TypeError(f"Invalid arguments, unsupported type for `{arg_name}`")

    else:
        raise TypeError(f"Invalid arguments, unsupported type for `{arg_name}`")

    return limiters


global_rate_limiters: list[Limiter] = []


def set_rate_limiters(limiters: list[Limiter]):
    global global_rate_limiters
    global_rate_limiters = limiters
