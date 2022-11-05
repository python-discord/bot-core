"""Helpers for setting a cooldown on commands."""

from __future__ import annotations

import asyncio
import random
import time
import typing
import weakref
from collections.abc import Awaitable, Callable, Hashable, Iterable
from contextlib import suppress
from dataclasses import dataclass

import discord
from discord.ext.commands import CommandError, Context

from pydis_core.utils import scheduling
from pydis_core.utils.function import command_wraps

__all__ = ["CommandOnCooldown", "block_duplicate_invocations", "P", "R"]

_KEYWORD_SEP_SENTINEL = object()

_ArgsList = list[object]
_HashableArgsTuple = tuple[Hashable, ...]

if typing.TYPE_CHECKING:
    import typing_extensions
    from pydis_core import BotBase

P = typing.ParamSpec("P")
"""The command's signature."""
R = typing.TypeVar("R")
"""The command's return value."""


class CommandOnCooldown(CommandError, typing.Generic[P, R]):
    """Raised when a command is invoked while on cooldown."""

    def __init__(
        self,
        message: str | None,
        function: Callable[P, Awaitable[R]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        super().__init__(message, function, args, kwargs)
        self._function = function
        self._args = args
        self._kwargs = kwargs

    async def call_without_cooldown(self) -> R:
        """
        Run the command this cooldown blocked.

        Returns:
            The command's return value.
        """
        return await self._function(*self._args, **self._kwargs)


@dataclass
class _CooldownItem:
    non_hashable_arguments: _ArgsList
    timeout_timestamp: float


@dataclass
class _SeparatedArguments:
    """Arguments separated into their hashable and non-hashable parts."""

    hashable: _HashableArgsTuple
    non_hashable: _ArgsList

    @classmethod
    def from_full_arguments(cls, call_arguments: Iterable[object]) -> typing_extensions.Self:
        """Create a new instance from full call arguments."""
        hashable = list[Hashable]()
        non_hashable = list[object]()

        for item in call_arguments:
            try:
                hash(item)
            except TypeError:
                non_hashable.append(item)
            else:
                hashable.append(item)

        return cls(tuple(hashable), non_hashable)


class _CommandCooldownManager:
    """
    Manage invocation cooldowns for a command through the arguments the command is called with.

    Use `set_cooldown` to set a cooldown,
    and `is_on_cooldown` to check for a cooldown for a channel with the given arguments.
    A cooldown lasts for `cooldown_duration` seconds.
    """

    def __init__(self, *, cooldown_duration: float):
        self._cooldowns = dict[tuple[Hashable, _HashableArgsTuple], list[_CooldownItem]]()
        self._cooldown_duration = cooldown_duration
        self.cleanup_task = scheduling.create_task(
            self._periodical_cleanup(random.uniform(0, 10)),
            name="CooldownManager cleanup",
        )
        weakref.finalize(self, self.cleanup_task.cancel)

    def set_cooldown(self, channel: Hashable, call_arguments: Iterable[object]) -> None:
        """Set `call_arguments` arguments on cooldown in `channel`."""
        timeout_timestamp = time.monotonic() + self._cooldown_duration
        separated_arguments = _SeparatedArguments.from_full_arguments(call_arguments)
        cooldowns_list = self._cooldowns.setdefault(
            (channel, separated_arguments.hashable),
            [],
        )

        for item in cooldowns_list:
            if item.non_hashable_arguments == separated_arguments.non_hashable:
                item.timeout_timestamp = timeout_timestamp
                return

        cooldowns_list.append(_CooldownItem(separated_arguments.non_hashable, timeout_timestamp))

    def is_on_cooldown(self, channel: Hashable, call_arguments: Iterable[object]) -> bool:
        """Check whether `call_arguments` is on cooldown in `channel`."""
        current_time = time.monotonic()
        separated_arguments = _SeparatedArguments.from_full_arguments(call_arguments)
        cooldowns_list = self._cooldowns.get(
            (channel, separated_arguments.hashable),
            [],
        )

        for item in cooldowns_list:
            if item.non_hashable_arguments == separated_arguments.non_hashable:
                return item.timeout_timestamp > current_time
        return False

    async def _periodical_cleanup(self, initial_delay: float) -> None:
        """
        Delete stale items every hour after waiting for `initial_delay`.

        The `initial_delay` ensures cleanups are not running for every command at the same time.
        A strong reference to self is only kept while cleanup is running.
        """
        weak_self = weakref.ref(self)
        del self

        await asyncio.sleep(initial_delay)
        while True:
            await asyncio.sleep(60 * 60)
            weak_self()._delete_stale_items()

    def _delete_stale_items(self) -> None:
        """Remove expired items from internal collections."""
        current_time = time.monotonic()

        for key, cooldowns_list in self._cooldowns.copy().items():
            filtered_cooldowns = [
                cooldown_item for cooldown_item in cooldowns_list if cooldown_item.timeout_timestamp < current_time
            ]

            if not filtered_cooldowns:
                del self._cooldowns[key]
            else:
                self._cooldowns[key] = filtered_cooldowns


def _create_argument_tuple(*args: object, **kwargs: object) -> tuple[object, ...]:
    return (*args, _KEYWORD_SEP_SENTINEL, *kwargs.items())


def block_duplicate_invocations(
    *,
    cooldown_duration: float = 5,
    send_notice: bool = False,
    args_preprocessor: Callable[P, Iterable[object]] | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Prevent duplicate invocations of a command with the same arguments in a channel for ``cooldown_duration`` seconds.

    Args:
        cooldown_duration: Length of the cooldown in seconds.
        send_notice: If :obj:`True`, notify the user about the cooldown with a reply.
        args_preprocessor: If specified, this function is called with the args and kwargs the function is called with,
                            its return value is then used to check for the cooldown instead of the raw arguments.

    Returns:
        A decorator that adds a wrapper which applies the cooldowns.

    Warning:
        The created wrapper raises :exc:`CommandOnCooldown` when the command is on cooldown.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        mgr = _CommandCooldownManager(cooldown_duration=cooldown_duration)

        @command_wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if args_preprocessor is not None:
                all_args = args_preprocessor(*args, **kwargs)
            else:
                all_args = _create_argument_tuple(*args[2:], **kwargs)  # skip self and ctx from the command
            ctx = typing.cast("Context[BotBase]", args[1])

            if not isinstance(ctx.channel, discord.DMChannel):
                if mgr.is_on_cooldown(ctx.channel, all_args):
                    if send_notice:
                        with suppress(discord.NotFound):
                            await ctx.reply("The command is on cooldown with the given arguments.")
                    raise CommandOnCooldown(ctx.message.content, func, *args, **kwargs)
                mgr.set_cooldown(ctx.channel, all_args)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
