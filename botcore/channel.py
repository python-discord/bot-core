"""Utilities for interacting with discord channels."""

import discord
from discord.ext.commands import Bot

from botcore import loggers

log = loggers.get_logger(__name__)


def is_in_category(channel: discord.TextChannel, category_id: int) -> bool:
    """Return True if `channel` is within a category with `category_id`."""
    return getattr(channel, "category_id", None) == category_id


async def get_or_fetch_channel(bot: Bot, channel_id: int) -> discord.abc.GuildChannel:
    """Attempt to get or fetch a channel and return it."""
    log.trace(f"Getting the channel {channel_id}.")

    channel = bot.get_channel(channel_id)
    if not channel:
        log.debug(f"Channel {channel_id} is not in cache; fetching from API.")
        channel = await bot.fetch_channel(channel_id)

    log.trace(f"Channel #{channel} ({channel_id}) retrieved.")
    return channel
