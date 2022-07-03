import json
import os
from typing import Any, Callable, TypeVar, overload


_T = TypeVar("_T")


@overload
def get_from_env(key: str, caster: None = None) -> str:
    ...


@overload
def get_from_env(key: str, caster: Callable[..., _T]) -> _T:
    ...


def get_from_env(key: str, caster: Any = None) -> Any:
    if caster is None:
        return os.getenv(key)
    return caster(os.getenv(key))


def deserialize_list(string: str) -> list[Any]:
    return json.loads(string)
