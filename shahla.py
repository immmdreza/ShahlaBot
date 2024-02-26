import functools
import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Self, cast

from pyrogram.client import Client
from pyrogram.errors import BadRequest
from pyrogram.types import Message, User
from telegram.ext import CallbackContext


class LifeTime(Enum):
    Singleton = "Singleton"
    Transient = "Transient"
    Scoped = "Scoped"


@dataclass()
class DependencyModel[T]:
    dependency_type: type[T]
    dependency_factory: Callable[..., T]
    dependency_lifetime: LifeTime
    dependency_instance: Optional[T] = None


class Scope[T]:
    def __init__(self, name: str, shahla: "Shahla", model: DependencyModel[T]):
        self._name = name
        self._shahla = shahla
        self._model = model
        self._dependency: Optional[T] = None

    def __enter__(self):
        if self._model.dependency_lifetime == LifeTime.Singleton:
            if self._model.dependency_instance is None:
                self._model.dependency_instance = self._model.dependency_factory(
                    self._shahla
                )
            return self._name, self._model.dependency_instance
        elif self._model.dependency_lifetime == LifeTime.Transient:
            return self._name, self._model.dependency_factory(self._shahla)
        else:
            self._dependency = self._model.dependency_factory(self._shahla)
            return self._name, self._dependency

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


class Shahla[T](Client):
    def register_type(
        self,
        the_type: type[T],
        instance_builder: Callable[[Self], T],
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

    def request_instance(self, the_type: type[T]) -> T:
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

    def create_scope_for(self, the_type: type[T], scope_name: str) -> Scope[T]:
        if not hasattr(self, "_registered_types"):
            raise ValueError("No registered types.")

        model = self._registered_types[the_type]
        return Scope(scope_name, self, model)

    async def resolve_target_user_from_command(self, message: Message) -> User | None:
        if message.command:
            if len(message.command) > 1:
                try:
                    return cast(User, await self.get_users(message.command[1]))
                except BadRequest:
                    return None

        if message.reply_to_message:
            if message.reply_to_message.from_user:
                return message.reply_to_message.from_user
            if message.reply_to_message.forward_from:
                return message.reply_to_message.forward_from
        return None

    async def resolve_target_user_and_others_from_command(
        self, message: Message
    ) -> tuple[User | None, list[str]]:
        if message.command:
            if len(message.command) > 2:
                if message.command[1].startswith("@") or message.command[1].isnumeric():
                    try:
                        return (
                            cast(User, await self.get_users(message.command[1])),
                            message.command[2:],
                        )
                    except BadRequest:
                        return None, message.command[2:]

        if message.reply_to_message:
            if message.reply_to_message.from_user:
                return (
                    message.reply_to_message.from_user,
                    message.command[1:],
                )
            if message.reply_to_message.forward_from:
                return (
                    message.reply_to_message.forward_from,
                    message.command[1:],
                )
        return (
            None,
            message.command[1:],
        )


def async_injector(func: Callable[..., Any]):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        signature = inspect.signature(func)
        args_count = len(args)

        shahla: Shahla | None = None
        try:
            shahla = next(x for x in args if isinstance(x, Shahla))
        except StopIteration:
            try:
                shahla = next(x for x in kwargs.values() if isinstance(x, Shahla))
            except StopIteration:
                raise ValueError("No shahla instance found.")

        resolved_types: dict[str, Scope[Any]] = {}
        for i, (key, value) in enumerate(signature.parameters.items()):
            if i <= (args_count - 1):
                continue

            if key in kwargs:
                continue

            instance = shahla.create_scope_for(value.annotation, key)
            resolved_types[key] = instance

        with MultipleScope(*resolved_types.values()) as scopes:
            return await func(*args, **kwargs, **dict(scopes))

    return wrapped


def injector(func: Callable[..., Any]):
    def wrapped(*args, **kwargs):
        signature = inspect.signature(func)
        args_count = len(args)

        shahla: Shahla | None = None
        try:
            shahla = next(x for x in args if isinstance(x, Shahla))
        except StopIteration:
            try:
                shahla = next(x for x in kwargs.values() if isinstance(x, Shahla))
            except StopIteration:
                raise ValueError("No shahla instance found.")

        resolved_types: dict[str, Scope[Any]] = {}
        for i, (key, value) in enumerate(signature.parameters.items()):
            if i <= (args_count - 1):
                continue

            if key in kwargs:
                continue

            instance = shahla.create_scope_for(value.annotation, key)
            resolved_types[key] = instance

        with MultipleScope(*resolved_types.values()) as scopes:
            return func(*args, **kwargs, **dict(scopes))

    return wrapped


def async_injector_grabber[
    K
](grab_from_type: type[K], grabber: Callable[[K], Shahla]) -> Callable[..., Any]:
    def async_injector(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            signature = inspect.signature(func)
            args_count = len(args)

            grab_from: K | None = None
            try:
                grab_from = next(x for x in args if isinstance(x, grab_from_type))
            except StopIteration:
                try:
                    grab_from = next(
                        x for x in kwargs.values() if isinstance(x, grab_from_type)
                    )
                except StopIteration:
                    raise ValueError("No shahla instance found.")
            shahla = grabber(grab_from)

            resolved_types: dict[str, Scope[Any]] = {}
            for i, (key, value) in enumerate(signature.parameters.items()):
                if i <= (args_count - 1):
                    continue

                if key in kwargs:
                    continue

                if value.annotation == grab_from_type:
                    continue

                if value.annotation == Shahla:
                    kwargs[key] = shahla

                instance = shahla.create_scope_for(value.annotation, key)
                resolved_types[key] = instance

            with MultipleScope(*resolved_types.values()) as scopes:
                return await func(*args, **kwargs, **dict(scopes))

        return wrapped

    return async_injector


def async_injector_from_ctx(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        signature = inspect.signature(func)
        args_count = len(args)

        try:
            grab_from = next(x for x in args if isinstance(x, CallbackContext))
        except StopIteration:
            try:
                grab_from = next(
                    x for x in kwargs.values() if isinstance(x, CallbackContext)
                )
            except StopIteration:
                raise ValueError("No shahla instance found.")
        shahla: Shahla = grab_from.bot_data["shahla"]

        resolved_types: dict[str, Scope[Any]] = {}
        for i, (key, value) in enumerate(signature.parameters.items()):
            if i <= (args_count - 1):
                continue

            if key in kwargs:
                continue

            if value.annotation == CallbackContext:
                continue

            if value.annotation == Shahla:
                kwargs[key] = shahla
                continue

            instance = shahla.create_scope_for(value.annotation, key)
            resolved_types[key] = instance

        with MultipleScope(*resolved_types.values()) as scopes:
            return await func(*args, **kwargs, **dict(scopes))

    return wrapped
