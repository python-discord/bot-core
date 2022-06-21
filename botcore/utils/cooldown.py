"""Helpers for setting a cooldown on commands."""

from __future__ import annotations

import asyncio
import math
import random
import time
import typing
from collections.abc import Awaitable, Hashable
from contextlib import suppress
from dataclasses import dataclass
from typing import Callable  # sphinx-autodoc-typehints breaks with collections.abc.Callable

import discord
from discord.ext.commands import CommandError, Context

from botcore.utils import scheduling
from botcore.utils.function import command_wraps

__all__ = ["CommandOnCooldown", "block_duplicate_invocations", "P", "R"]

_ArgsTuple = tuple[object, ...]

if typing.TYPE_CHECKING:
    from botcore import BotBase
    import typing_extensions
    P = typing_extensions.ParamSpec("P")
    P.__constraints__ = ()
else:
    P = typing.TypeVar("P")
    """The command's signature."""

R = typing.TypeVar("R")
"""The command's return value."""


class CommandOnCooldown(CommandError, typing.Generic[P, R]):
    """Raised when a command is invoked while on cooldown."""

    def __init__(
        self,
        message: str | None,
        function: Callable[P, Awaitable[R]],
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
    call_arguments: _ArgsTuple
    timeout_timestamp: float


class _CommandCooldownManager:
    """
    Manage invocation cooldowns for a command through the arguments the command is called with.

    Use `set_cooldown` to set a cooldown,
    and `is_on_cooldown` to check for a cooldown for a channel with the given arguments.
    A cooldown lasts for `cooldown_duration` seconds.
    """

    def __init__(self, *, cooldown_duration: float):
        self._cooldowns = dict[tuple[Hashable, _ArgsTuple], float]()
        self._cooldowns_non_hashable = dict[Hashable, list[_CooldownItem]]()
        self._cooldown_duration = cooldown_duration
        self.cleanup_task = scheduling.create_task(
            self._periodical_cleanup(random.uniform(0, 10)),
            name="CooldownManager cleanup",
        )

    def set_cooldown(self, channel: Hashable, call_arguments: _ArgsTuple) -> None:
        """Set `call_arguments` arguments on cooldown in `channel`."""
        timeout_timestamp = time.monotonic() + self._cooldown_duration

        try:
            self._cooldowns[(channel, call_arguments)] = timeout_timestamp
        except TypeError:
            cooldowns_list = self._cooldowns_non_hashable.setdefault(channel, [])
            for item in cooldowns_list:
                if item.call_arguments == call_arguments:
                    item.timeout_timestamp = timeout_timestamp
            else:
                cooldowns_list.append(_CooldownItem(call_arguments, timeout_timestamp))

    def is_on_cooldown(self, channel: Hashable, call_arguments: _ArgsTuple) -> bool:
        """Check whether `call_arguments` is on cooldown in `channel`."""
        current_time = time.monotonic()
        try:
            return self._cooldowns.get((channel, call_arguments), -math.inf) > current_time
        except TypeError:
            cooldowns_list = self._cooldowns_non_hashable.get(channel, None)
            if cooldowns_list is None:
                return False

            for item in cooldowns_list:
                if item.call_arguments == call_arguments:
                    return item.timeout_timestamp > current_time
            return False

    async def _periodical_cleanup(self, initial_delay: float) -> None:
        """
        Delete stale items every hour after waiting for `initial_delay`.

        The `initial_delay` ensures cleanups are not running for every command at the same time.
        """
        await asyncio.sleep(initial_delay)
        while True:
            await asyncio.sleep(60 * 60)
            self._delete_stale_items()

    def _delete_stale_items(self) -> None:
        """Remove expired items from internal collections."""
        current_time = time.monotonic()

        for key, timeout_timestamp in self._cooldowns.copy().items():
            if timeout_timestamp < current_time:
                del self._cooldowns[key]

        for key, cooldowns_list in self._cooldowns_non_hashable.copy().items():
            filtered_cooldowns = [
                cooldown_item for cooldown_item in cooldowns_list if cooldown_item.timeout_timestamp < current_time
            ]

            if not filtered_cooldowns:
                del self._cooldowns_non_hashable[key]
            else:
                self._cooldowns_non_hashable[key] = filtered_cooldowns


def block_duplicate_invocations(
    *, cooldown_duration: float = 5, send_notice: bool = False
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Prevent duplicate invocations of a command with the same arguments in a channel for ``cooldown_duration`` seconds.

    Args:
        cooldown_duration: Length of the cooldown in seconds.
        send_notice: If :obj:`True`, notify the user about the cooldown with a reply.

    Returns:
        A decorator that adds a wrapper which applies the cooldowns.

    Warning:
        The created wrapper raises :exc:`CommandOnCooldown` when the command is on cooldown.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        mgr = _CommandCooldownManager(cooldown_duration=cooldown_duration)

        @command_wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            arg_tuple = (*args[2:], *kwargs.items())  # skip self and ctx from the command
            ctx = typing.cast("Context[BotBase]", args[1])
            channel = ctx.channel

            if not isinstance(channel, discord.DMChannel):
                if mgr.is_on_cooldown(ctx.channel, arg_tuple):
                    if send_notice:
                        with suppress(discord.NotFound):
                            await ctx.reply("The command is on cooldown with the given arguments.")
                    raise CommandOnCooldown(ctx.message.content, func, *args, **kwargs)
                mgr.set_cooldown(ctx.channel, arg_tuple)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
