from typing import Optional

from discord import Message
from discord.ext.commands import BadArgument, Context, clean_content


async def clean_text_or_reply(ctx: Context, text: Optional[str] = None) -> str:
    """
    Cleans a text argument or replied message's content.

    Args:
        ctx: The command's context
        text: The provided text argument of the command (if given)

    Raises:
        :exc:`discord.ext.commands.BadArgument`
            `text` wasn't provided and there's no reply message.

    Returns:
         The cleaned version of `text`, if given, else replied message.
    """
    clean_content_converter = clean_content(fix_channel_mentions=True)

    if text:
        return await clean_content_converter.convert(ctx, text)

    if (
        (replied_message := getattr(ctx.message.reference, "resolved", None))  # message has a cached reference
        and isinstance(replied_message, Message)  # referenced message hasn't been deleted
    ):
        return await clean_content_converter.convert(ctx, ctx.message.reference.resolved.content)

    # No text provided, and either no message was referenced or we can't access the content
    raise BadArgument("Couldn't find text to clean. Provide a string or reply to a message to use its content.")
