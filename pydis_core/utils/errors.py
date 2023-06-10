from discord import Forbidden, Message

from pydis_core.utils import logging

log = logging.get_logger(__name__)


async def handle_forbidden_from_block(error: Forbidden, message: Message | None = None) -> None:
    """
    Handles ``discord.Forbidden`` 90001 errors, or re-raises if ``error`` isn't a 90001 error.

    Args:
        error: The raised ``discord.Forbidden`` to check.
        message: The message to reply to and include in logs, if error is 90001 and message is provided.
    """
    if error.code != 90001:
        # The error ISN'T caused by the bot attempting to add a reaction
        # to a message whose author has blocked the bot, so re-raise it
        raise error

    if not message:
        log.info("Failed to add reaction(s) to a message since the message author has blocked the bot")
        return

    if message:
        log.info(
            "Failed to add reaction(s) to message %d-%d since the message author (%d) has blocked the bot",
            message.channel.id,
            message.id,
            message.author.id,
        )
        await message.channel.send(
            f":x: {message.author.mention} failed to add reaction(s) to your message as you've blocked me.",
            delete_after=30
        )
