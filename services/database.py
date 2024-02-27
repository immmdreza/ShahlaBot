from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Optional,
    TypeVar,
)

import pymongo.collection
import pymongo.mongo_client

from models import ModelBase
from models._filter_builder import _FilterBuilder
from models.configuration import Configuration
from models.extra_info import ExtraInfo
from models.game_info import GameInfo
from models.group_admin import GroupAdmin
from models.user_warnings import UserWarning

T = TypeVar("T", bound=ModelBase)


class Collection(Generic[T]):
    def __init__(
        self, entity_type: type[T], collection: pymongo.collection.Collection
    ):
        self._entity_type = entity_type
        self._collection = collection

    @property
    def collection(self) -> pymongo.collection.Collection:
        return self._collection

    def find(self, *args: Any, **kwargs: Any) -> Generator[T, None, None]:
        return (
            x
            for x in (
                self._entity_type.deserialize(item)
                for item in self._collection.find(*args, **kwargs)
            )
            if x is not None
        )

    def find_one(self, *args: Any, **kwargs: Any) -> Optional[T]:
        return self._entity_type.deserialize(
            self._collection.find_one(*args, **kwargs)
        )

    def find_one_by_filter(
        self,
        filter: Callable[[_FilterBuilder[T]], Any],
        *args: Any,
        **kwargs: Any
    ) -> Optional[T]:
        flt = _FilterBuilder(self._entity_type)
        filter(flt)
        return self._entity_type.deserialize(
            self._collection.find_one(flt.build(), *args, **kwargs)
        )

    def insert_one(self, document: T, *args: Any, **kwargs: Any):
        return self._collection.insert_one(
            document.serialize(), *args, **kwargs
        )

    def insert_many(self, documents: Iterable[T], *args: Any, **kwargs: Any):
        return self._collection.insert_many(
            (document.serialize() for document in documents), *args, **kwargs
        )

    def update_model(self, update: T, *args: Any, **kwargs: Any):
        flt = {"_id": update.id}
        return self.update_one(
            flt, {"$set": update.serialize()}, *args, **kwargs
        )

    def update_one(self, filter: Any, update: Any, *args: Any, **kwargs: Any):
        return self._collection.update_one(filter, update, *args, **kwargs)

    def update_many(self, filter: Any, update: Any, *args: Any, **kwargs: Any):
        return self._collection.update_many(filter, update, *args, **kwargs)

    def delete_one(self, filter: Any, *args: Any, **kwargs: Any):
        return self._collection.delete_one(filter, *args, **kwargs)

    def delete_many(self, filter: Any, *args: Any, **kwargs: Any):
        return self._collection.delete_many(filter, *args, **kwargs)

    def exists(self, filter: Any, *args: Any, **kwargs: Any) -> bool:
        return self._collection.count_documents(filter, *args, **kwargs) > 0


class Database:
    def __init__(self, __name: str | None = None, __host: str | None = None):
        self.client = pymongo.mongo_client.MongoClient[dict[str, Any]](__host)
        self.db = self.client.get_database(__name)

        self._configurations: Optional[Collection[Configuration]] = None
        self._user_warnings: Optional[Collection[UserWarning]] = None
        self._group_admins: Optional[Collection[GroupAdmin]] = None
        self._extra_infos: Optional[Collection[ExtraInfo]] = None
        self._game_infos: Optional[Collection[GameInfo]] = None

    def get_collection(self, entity_type: type[T]) -> Collection[T]:
        return Collection(
            entity_type, self.db.get_collection(entity_type.__name__)
        )

    @property
    def configurations(self) -> Collection[Configuration]:
        if self._configurations is None:
            self._configurations = self.get_collection(Configuration)
        return self._configurations

    @property
    def user_warnings(self) -> Collection[UserWarning]:
        if self._user_warnings is None:
            self._user_warnings = self.get_collection(UserWarning)
        return self._user_warnings

    @property
    def group_admins(self) -> Collection[GroupAdmin]:
        if self._group_admins is None:
            self._group_admins = self.get_collection(GroupAdmin)
        return self._group_admins

    @property
    def extra_infos(self) -> Collection[ExtraInfo]:
        if self._extra_infos is None:
            self._extra_infos = self.get_collection(ExtraInfo)
        return self._extra_infos

    @property
    def game_infos(self) -> Collection[GameInfo]:
        if self._game_infos is None:
            self._game_infos = self.get_collection(GameInfo)
        return self._game_infos

    def set_up(self, config: Configuration):
        col = self.configurations
        col.collection.drop()

        col.insert_one(config)
        return config
