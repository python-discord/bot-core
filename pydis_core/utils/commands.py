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
            `text` wasn't provided and there's no reply message / reply message content.

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
        if not (content := ctx.message.reference.resolved.content):
            # The referenced message doesn't have a content (e.g. embed/image), so raise error
            raise BadArgument("The referenced message doesn't have a text content.")

        return await clean_content_converter.convert(ctx, content)

    # No text provided, and either no message was referenced or we can't access the content
    raise BadArgument("Couldn't find text to clean. Provide a string or reply to a message to use its content.")
