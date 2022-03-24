import asyncio
import socket
import types
from abc import abstractmethod
from contextlib import suppress
from typing import Optional

import aiohttp
import discord
from async_rediscache import RedisSession
from discord.ext import commands

from botcore.async_stats import AsyncStatsClient
from botcore.site_api import APIClient
from botcore.utils._extensions import walk_extensions
from botcore.utils.logging import get_logger

log = get_logger()


class StartupError(Exception):
    """Exception class for startup errors."""

    def __init__(self, base: Exception):
        super().__init__()
        self.exception = base


class BotBase(commands.Bot):
    """A sub-class that implements many common features that Python Discord bots use."""

    def __init__(
        self,
        *args,
        guild_id: int,
        allowed_roles: list,
        http_session: aiohttp.ClientSession,
        redis_session: Optional[RedisSession] = None,
        **kwargs,
    ):
        """
        Initialise the base bot instance.

        Args:
            guild_id: The ID of the guild use for :func:`wait_until_guild_available`.
            allowed_roles: A list of role IDs that the bot is allowed to mention.
            http_session (aiohttp.ClientSession): The session to use for the bot.
            redis_session: The
                ``[async_rediscache.RedisSession](https://github.com/SebastiaanZ/async-rediscache#creating-a-redissession)``
                to use for the bot.
        """
        super().__init__(
            *args,
            allowed_roles=allowed_roles,
            **kwargs,
        )

        self.guild_id = guild_id
        self.http_session = http_session
        if redis_session:
            self.redis_session = redis_session

        self.api_client: Optional[APIClient] = None

        self._resolver = aiohttp.AsyncResolver()
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )
        self.http.connector = self._connector

        self.statsd_url: Optional[str] = None
        self._statsd_timerhandle: Optional[asyncio.TimerHandle] = None
        self._guild_available = asyncio.Event()

        self.stats: Optional[AsyncStatsClient] = None

    def _connect_statsd(
        self,
        statsd_url: str,
        loop: asyncio.AbstractEventLoop,
        retry_after: int = 2,
        attempt: int = 1
    ) -> None:
        """Callback used to retry a connection to statsd if it should fail."""
        if attempt >= 8:
            log.error("Reached 8 attempts trying to reconnect AsyncStatsClient. Aborting")
            return

        try:
            self.stats = AsyncStatsClient(loop, statsd_url, 8125, prefix="bot")
        except socket.gaierror:
            log.warning(f"Statsd client failed to connect (Attempt(s): {attempt})")
            # Use a fallback strategy for retrying, up to 8 times.
            self._statsd_timerhandle = loop.call_later(
                retry_after,
                self._connect_statsd,
                statsd_url,
                retry_after * 2,
                attempt + 1
            )

        # All tasks that need to block closing until finished
        self.closing_tasks: list[asyncio.Task] = []

    async def load_extensions(self, module: types.ModuleType) -> None:
        """Load all the extensions within the given module."""
        for extension in walk_extensions(module):
            await self.load_extension(extension)

    def _add_root_aliases(self, command: commands.Command) -> None:
        """Recursively add root aliases for ``command`` and any of its subcommands."""
        if isinstance(command, commands.Group):
            for subcommand in command.commands:
                self._add_root_aliases(subcommand)

        for alias in getattr(command, "root_aliases", ()):
            if alias in self.all_commands:
                raise commands.CommandRegistrationError(alias, alias_conflict=True)

            self.all_commands[alias] = command

    def _remove_root_aliases(self, command: commands.Command) -> None:
        """Recursively remove root aliases for ``command`` and any of its subcommands."""
        if isinstance(command, commands.Group):
            for subcommand in command.commands:
                self._remove_root_aliases(subcommand)

        for alias in getattr(command, "root_aliases", ()):
            self.all_commands.pop(alias, None)

    async def add_cog(self, cog: commands.Cog) -> None:
        """Adds the given ``cog`` to the bot and logs the operation."""
        await super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    def add_command(self, command: commands.Command) -> None:
        """Add ``command`` as normal and then add its root aliases to the bot."""
        super().add_command(command)
        self._add_root_aliases(command)

    def remove_command(self, name: str) -> Optional[commands.Command]:
        """
        Remove a command/alias as normal and then remove its root aliases from the bot.

        Individual root aliases cannot be removed by this function.
        To remove them, either remove the entire command or manually edit `bot.all_commands`.
        """
        command = super().remove_command(name)
        if command is None:
            # Even if it's a root alias, there's no way to get the Bot instance to remove the alias.
            return None

        self._remove_root_aliases(command)
        return command

    def clear(self) -> None:
        """Not implemented! Re-instantiate the bot instead of attempting to re-use a closed one."""
        raise NotImplementedError("Re-using a Bot object after closing it is not supported.")

    async def on_guild_unavailable(self, guild: discord.Guild) -> None:
        """Clear the internal guild available event when self.guild_id becomes unavailable."""
        if guild.id != self.guild_id:
            return

        self._guild_available.clear()

    async def on_guild_available(self, guild: discord.Guild) -> None:
        """
        Set the internal guild available event when self.guild_id becomes available.

        If the cache appears to still be empty (no members, no channels, or no roles), the event
        will not be set and `guild_available_but_cache_empty` event will be emitted.
        """
        if guild.id != self.guild_id:
            return

        if not guild.roles or not guild.members or not guild.channels:
            msg = "Guild available event was dispatched but the cache appears to still be empty!"
            self.log_to_dev_log(msg)
            return

        self._guild_available.set()

    @abstractmethod
    async def log_to_dev_log(self, message: str) -> None:
        """Log the given message to #dev-log."""
        ...

    async def wait_until_guild_available(self) -> None:
        """
        Wait until the guild that matches the ``guild_id`` given at init is available (and the cache is ready).

        The on_ready event is inadequate because it only waits 2 seconds for a GUILD_CREATE
        gateway event before giving up and thus not populating the cache for unavailable guilds.
        """
        await self._guild_available.wait()

    async def setup_hook(self) -> None:
        """
        An async init to startup generic services.

        Connects to statsd, and calls
        :func:`AsyncStatsClient.create_socket <botcore.async_stats.AsyncStatsClient.create_socket>`
        and :func:`ping_services`.
        """
        loop = asyncio.get_running_loop()
        self._connect_statsd(self.statsd_url, loop)
        self.stats = AsyncStatsClient(loop, "127.0.0.1")
        await self.stats.create_socket()

        try:
            await self.ping_services()
        except Exception as e:
            raise StartupError(e)

    @abstractmethod
    async def ping_services() -> None:
        """Ping all required services on setup to ensure they are up before starting."""
        ...

    async def close(self) -> None:
        """Close the Discord connection, and the aiohttp session, connector, statsd client, and resolver."""
        # Done before super().close() to allow tasks finish before the HTTP session closes.
        for ext in list(self.extensions):
            with suppress(Exception):
                await self.unload_extension(ext)

        for cog in list(self.cogs):
            with suppress(Exception):
                await self.remove_cog(cog)

        # Wait until all tasks that have to be completed before bot is closing is done
        log.trace("Waiting for tasks before closing.")
        await asyncio.gather(*self.closing_tasks)

        # Now actually do full close of bot
        await super().close()

        if self.api_client:
            await self.api_client.close()

        if self.http_session:
            await self.http_session.close()

        if self._connector:
            await self._connector.close()

        if self._resolver:
            await self._resolver.close()

        if self.stats._transport:
            self.stats._transport.close()

        if self.redis_session:
            await self.redis_session.close()

        if self._statsd_timerhandle:
            self._statsd_timerhandle.cancel()
