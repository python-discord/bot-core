"""Useful helper functions for interacting with various discord channel objects."""

import discord
from discord.ext.commands import Bot

from pydis_core.utils import logging

log = logging.get_logger(__name__)


def is_in_category(channel: discord.TextChannel, category_id: int) -> bool:
    """
    Return whether the given ``channel`` in the the category with the id ``category_id``.

    Args:
        channel: The channel to check.
        category_id: The category to check for.

    Returns:
        A bool depending on whether the channel is in the category.
    """
    return getattr(channel, "category_id", None) == category_id


async def get_or_fetch_channel(bot: Bot, channel_id: int) -> discord.abc.GuildChannel:
    """
    Attempt to get or fetch the given ``channel_id`` from the bots cache, and return it.

    Args:
        bot: The :obj:`discord.ext.commands.Bot` instance to use for getting/fetching.
        channel_id: The channel to get/fetch.

    Raises:
        :exc:`discord.InvalidData`
            An unknown channel type was received from Discord.
        :exc:`discord.HTTPException`
            Retrieving the channel failed.
        :exc:`discord.NotFound`
            Invalid Channel ID.
        :exc:`discord.Forbidden`
            You do not have permission to fetch this channel.

    Returns:
        The channel from the ID.
    """
    log.trace(f"Getting the channel {channel_id}.")

    channel = bot.get_channel(channel_id)
    if not channel:
        log.debug(f"Channel {channel_id} is not in cache; fetching from API.")
        channel = await bot.fetch_channel(channel_id)

    log.trace(f"Channel #{channel} ({channel_id}) retrieved.")
    return channel
