from dataclasses import Field
from typing import Any, Callable, Generic, Optional, TypeVar


_T = TypeVar("_T")
_TAny = TypeVar("_TAny", bound=Any)


class _FilterBuilder(Generic[_T]):
    def __init__(self, model_type: type[_T]):
        self._model_type = model_type
        self._filter = {}

    def add(
        self,
        selector: Callable[[type[_T]], _TAny],
        value: _TAny,
        operator: Optional[str] = None,
    ):
        prop = selector(self._model_type)
        if isinstance(prop, Field):
            if operator is None:
                self._filter[prop.name] = value
            else:
                self._filter[operator] = {prop.name: value}
        else:
            raise ValueError(f"{self._model_type} has no field {prop}")
        return self

    def build(self) -> dict[str, Any]:
        return self._filter
