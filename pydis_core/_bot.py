import asyncio
import socket
import types
import warnings
from contextlib import suppress
from typing import Optional

import aiohttp
import discord
from discord.ext import commands

from pydis_core.async_stats import AsyncStatsClient
from pydis_core.site_api import APIClient
from pydis_core.utils import scheduling
from pydis_core.utils._extensions import walk_extensions
from pydis_core.utils.logging import get_logger

try:
    from async_rediscache import RedisSession
    REDIS_AVAILABLE = True
except ImportError:
    RedisSession = None
    REDIS_AVAILABLE = False

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
        api_client: Optional[APIClient] = None,
        statsd_url: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialise the base bot instance.

        Args:
            guild_id: The ID of the guild used for :func:`wait_until_guild_available`.
            allowed_roles: A list of role IDs that the bot is allowed to mention.
            http_session (aiohttp.ClientSession): The session to use for the bot.
            redis_session: The `async_rediscache.RedisSession`_ to use for the bot.
            api_client: The :obj:`pydis_core.site_api.APIClient` instance to use for the bot.
            statsd_url: The URL of the statsd server to use for the bot. If not given,
                a dummy statsd client will be created.

        .. _async_rediscache.RedisSession: https://github.com/SebastiaanZ/async-rediscache#creating-a-redissession
        """
        super().__init__(
            *args,
            allowed_roles=allowed_roles,
            **kwargs,
        )

        self.guild_id = guild_id
        self.http_session = http_session
        self.api_client = api_client
        self.statsd_url = statsd_url

        if redis_session and not REDIS_AVAILABLE:
            warnings.warn("redis_session kwarg passed, but async-rediscache not installed!", stacklevel=2)
        elif redis_session:
            self.redis_session = redis_session

        self._resolver: Optional[aiohttp.AsyncResolver] = None
        self._connector: Optional[aiohttp.TCPConnector] = None

        self._statsd_timerhandle: Optional[asyncio.TimerHandle] = None
        self._guild_available: Optional[asyncio.Event] = None
        self._extension_loading_task: asyncio.Task | None = None

        self.stats: Optional[AsyncStatsClient] = None

        self.all_extensions: Optional[frozenset[str]] = None

    def _connect_statsd(
        self,
        statsd_url: str,
        loop: asyncio.AbstractEventLoop,
        retry_after: int = 2,
        attempt: int = 1
    ) -> None:
        """Callback used to retry a connection to statsd if it should fail."""
        if attempt >= 8:
            log.error(
                "Reached 8 attempts trying to reconnect AsyncStatsClient to %s. "
                "Aborting and leaving the dummy statsd client in place.",
                statsd_url,
            )
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

    async def _load_extensions(self, module: types.ModuleType) -> None:
        """Load all the extensions within the given module and save them to ``self.all_extensions``."""
        await self.wait_until_guild_available()
        self.all_extensions = walk_extensions(module)

        for extension in self.all_extensions:
            scheduling.create_task(self.load_extension(extension))

    async def _sync_app_commands(self) -> None:
        """Sync global & guild specific application commands after extensions are loaded."""
        await self._extension_loading_task
        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(self.guild_id))

    async def load_extensions(self, module: types.ModuleType, sync_app_commands: bool = True) -> None:
        """
        Load all the extensions within the given ``module`` and save them to ``self.all_extensions``.

        Args:
            sync_app_commands: Whether to sync app commands after all extensions are loaded.
        """
        self._extension_loading_task = scheduling.create_task(self._load_extensions(module))
        if sync_app_commands:
            scheduling.create_task(self._sync_app_commands())

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
        """Add the given ``cog`` to the bot and log the operation."""
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
            await self.log_to_dev_log(msg)
            return

        self._guild_available.set()

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
        :func:`AsyncStatsClient.create_socket <pydis_core.async_stats.AsyncStatsClient.create_socket>`
        and :func:`ping_services`.
        """
        loop = asyncio.get_running_loop()

        self._guild_available = asyncio.Event()

        self._resolver = aiohttp.AsyncResolver()
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )
        self.http.connector = self._connector

        if getattr(self, "redis_session", False) and not self.redis_session.valid:
            # If the RedisSession was somehow closed, we try to reconnect it
            # here. Normally, this shouldn't happen.
            await self.redis_session.connect(ping=True)

        # Create dummy stats client first, in case `statsd_url` is unreachable or None
        self.stats = AsyncStatsClient(loop, "127.0.0.1")
        if self.statsd_url:
            self._connect_statsd(self.statsd_url, loop)

        await self.stats.create_socket()

        try:
            await self.ping_services()
        except Exception as e:
            raise StartupError(e)

    async def ping_services(self) -> None:
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

        if getattr(self.stats, "_transport", False):
            self.stats._transport.close()

        if self._statsd_timerhandle:
            self._statsd_timerhandle.cancel()
