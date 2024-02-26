from dataclasses import asdict, dataclass, field
from typing import Any, Self

from bson.objectid import ObjectId

from ._filter_builder import _FilterBuilder


def deserialize[T](cls: type[T], data: dict[str, Any] | None) -> T | None:
    if data is None:
        return None
    return cls(**data)


@dataclass()
class ModelBase:
    _id: ObjectId | None = field(default=None, kw_only=True)

    def serialize(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None and k != "_id"}

    @classmethod
    def deserialize(cls, data: dict[str, Any] | None) -> Self | None:
        return deserialize(cls, data)

    @property
    def id(self) -> ObjectId:
        if self._id is None:
            raise ValueError(f"{self} has no id")
        return self._id

    @classmethod
    def get_filter_builder(cls):
        return _FilterBuilder(cls)
