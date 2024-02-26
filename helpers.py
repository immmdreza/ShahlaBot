import json
import os
import re
from datetime import timedelta
from typing import Any, Callable, overload


@overload
def get_from_env(key: str, caster: None = None) -> str: ...


@overload
def get_from_env[T](key: str, caster: Callable[..., T]) -> T: ...


def get_from_env(key: str, caster: Any = None) -> Any:
    if caster is None:
        return os.getenv(key)
    return caster(os.getenv(key))


def deserialize_list(string: str) -> list[Any]:
    return json.loads(string)


_TIME_REGEX = re.compile(
    r"((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
)


def parse_time(time_str: str) -> timedelta | None:
    parts = _TIME_REGEX.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)
