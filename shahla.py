from dataclasses import dataclass
from enum import Enum
import functools
import inspect
from typing import Any, Callable, Generic, Optional, TypeVar

import pyrogram.client


_T = TypeVar("_T")


class LifeTime(Enum):
    Singleton = "Singleton"
    Transient = "Transient"
    Scoped = "Scoped"


@dataclass()
class DependencyModel(Generic[_T]):
    dependency_type: type[_T]
    dependency_factory: Callable[..., _T]
    dependency_lifetime: LifeTime
    dependency_instance: Optional[_T] = None


class Scope(Generic[_T]):
    def __init__(self, shahla: "Shahla", model: DependencyModel[_T]):
        self._shahla = shahla
        self._model = model
        self._dependency: Optional[_T] = None

    def __enter__(self):
        if self._model.dependency_lifetime == LifeTime.Singleton:
            if self._model.dependency_instance is None:
                self._model.dependency_instance = self._model.dependency_factory(
                    self._shahla
                )
            return self._model.dependency_instance
        elif self._model.dependency_lifetime == LifeTime.Transient:
            return self._model.dependency_factory(self._shahla)
        else:
            self._dependency = self._model.dependency_factory(self._shahla)
            return self._dependency

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._model.dependency_lifetime == LifeTime.Scoped:
            if hasattr(self._dependency, "__exit__"):
                self._dependency.__exit__(exc_type, exc_val, exc_tb)  # type: ignore
            del self._dependency
            self._dependency = None


class MultipleScope:
    def __init__(self, *scopes: Scope[Any]):
        self._scopes = scopes

    def __enter__(self):
        return tuple(scope.__enter__() for scope in self._scopes)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for scope in self._scopes:
            scope.__exit__(exc_type, exc_val, exc_tb)


class Shahla(pyrogram.client.Client):
    def register_type(
        self,
        the_type: type[_T],
        instance_builder: Callable[["Shahla"], _T],
        lifetime: LifeTime = LifeTime.Singleton,
    ):
        if not hasattr(self, "_registered_types"):
            self._registered_types: dict[type[Any], DependencyModel[Any]] = {}

        if the_type in self._registered_types:
            raise ValueError(f"Type {the_type} already registered.")

        if lifetime == LifeTime.Singleton:
            built = instance_builder(self)
            model = DependencyModel(the_type, instance_builder, lifetime, built)
            self._registered_types[the_type] = model
        else:
            model = DependencyModel(the_type, instance_builder, lifetime)
            self._registered_types[the_type] = model

    def request_instance(self, the_type: type[_T]) -> _T:
        if not hasattr(self, "_registered_types"):
            raise ValueError("No registered types.")

        try:
            model = self._registered_types[the_type]
            if model.dependency_lifetime == LifeTime.Singleton:
                if model.dependency_instance is None:
                    model.dependency_instance = model.dependency_factory(self)
                return model.dependency_instance
            elif model.dependency_lifetime == LifeTime.Transient:
                return model.dependency_factory(self)
            else:
                raise ValueError("Unsupported lifetime.")
        except KeyError:
            raise ValueError(f"Type {the_type} not registered.")

    def create_scope_for(self, the_type: type[_T]) -> Scope[_T]:
        if not hasattr(self, "_registered_types"):
            raise ValueError("No registered types.")

        model = self._registered_types[the_type]
        return Scope(self, model)


def async_injector(func: Callable[..., Any]):
    @functools.wraps(func)
    async def wrapped(self: Shahla, update: Any):
        signature = inspect.signature(func)

        resolved_types: dict[str, Scope[Any]] = {}
        for i, (key, value) in enumerate(signature.parameters.items()):
            if i <= 1:
                continue

            instance = self.create_scope_for(value.annotation)
            resolved_types[key] = instance

        with MultipleScope(*resolved_types.values()) as scopes:
            return await func(self, update, *scopes)

    return wrapped
