"""Useful helper functions for interacting with various discord.py channel objects."""

import discord
from discord.ext.commands import Bot

from botcore.utils import logging

log = logging.get_logger(__name__)


def is_in_category(channel: discord.TextChannel, category_id: int) -> bool:
    """
    Return whether the given channel has the category_id.

    Args:
        channel: The channel to check.
        category_id: The category to check for.

    Returns:
        A bool depending on whether the channel is in the category.
    """
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
