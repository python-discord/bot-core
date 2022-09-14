from asyncio import TimeoutError
from contextlib import suppress
from typing import Optional

from discord import HTTPException, Message, NotFound
from discord.ext.commands import BadArgument, Context, clean_content


REDO_EMOJI = '\U0001f501'  # :repeat:
REDO_TIMEOUT = 30


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


async def check_rerun_job(ctx: Context, response: Message) -> Optional[str]:
    """
    Check if the job should be rerun.

    For a job to be rerun, the user must edit their message within ``REDO_TIMEOUT`` seconds,
    and then react with the ``REDO_EMOJI`` within 10 seconds.

    Args:
        ctx: The command's context
        response: The job's response message

    Returns:
         The content to be rerun, or ``None``.
    """
    # Correct message and content did actually change (i.e. wasn't a pin status udpate etc.)
    _message_edit_predicate = lambda old, new: new.id == ctx.message.id and new.content != old.content

    _reaction_add_predicate = lambda reaction, user: all((
        user.id == ctx.author.id,  # correct user
        str(reaction) == REDO_EMOJI,  # correct emoji
        reaction.message.id == ctx.message.id  # correct message
    ))

    with suppress(NotFound):
        try:
            _, new_message = await ctx.bot.wait_for(
                'message_edit',
                check=_message_edit_predicate,
                timeout=REDO_TIMEOUT
            )
            await ctx.message.add_reaction(REDO_EMOJI)

            await ctx.bot.wait_for(
                'reaction_add',
                check=_reaction_add_predicate,
                timeout=10
            )

            await ctx.message.clear_reaction(REDO_EMOJI)
            with suppress(HTTPException):
                await response.delete()

        except TimeoutError:
            # One of the `wait_for` timed out, so abort since user doesn't want to rerun
            await ctx.message.clear_reaction(REDO_EMOJI)
            return None

        else:
            # Both `wait_for` triggered, so return the new content to be run since user wants to rerun
            return new_message.content

    return None  # triggered whenever a `NotFound` was raised
