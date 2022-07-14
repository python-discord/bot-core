from typing import Optional

from discord import Message
from discord.ext.commands import Context, clean_content


async def clean_text_or_reply(ctx: Context, text: Optional[str] = None) -> Optional[str]:
    """Returns cleaned version of `text`, if given, else referenced message, if found, else `None`."""
    clean_content_converter = clean_content(fix_channel_mentions=True)

    if text:
        return await clean_content_converter.convert(ctx, text)

    if (
        (replied_message := getattr(ctx.message.reference, "resolved", None))  # message has a cached reference
        and isinstance(replied_message, Message)  # referenced message hasn't been deleted
    ):
        return await clean_content_converter.convert(ctx, ctx.message.reference.resolved.content)

    # No text provided, and either no message was referenced or we can't access the content
    return None
