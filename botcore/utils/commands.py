from asyncio import TimeoutError
from contextlib import suppress
from itertools import zip_longest
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


async def check_rerun_command(ctx: Context, response: Message) -> None:
    """
    Check if the command should be rerun (and reruns if should be).

    For a command to be rerun, the user must edit their invocation message within
    ``REDO_TIMEOUT`` seconds, and then react with the ``REDO_EMOJI`` within 10 seconds.

    Args:
        ctx: The command's context
        response: The job's response message
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
            return

        else:
            # Both `wait_for` triggered, so return the new content to be run since user wants to rerun

            # Determine if the edited message starts with a valid prefix, and if it does store it
            prefix_or_prefixes = await ctx.bot.get_prefix(ctx.message)
            active_prefix = None
            if isinstance(prefix_or_prefixes, list):
                # Bot is listening to multiple prefixes
                for prefix in prefix_or_prefixes:
                    if ctx.message.content.startswith(prefix):
                        active_prefix = prefix
                        break
                else:
                    await ctx.reply(":warning: Stopped listening because you removed the prefix.")
                    return False
            else:
                # Bot is only listening to one prefix
                if not new_message.content.startswith(prefix_or_prefixes):
                    await ctx.reply(":warning: Stopped listening because you removed the prefix.")
                    return
                active_prefix = prefix_or_prefixes

            # The edited content has a valid prefix, so remove it
            content = new_message.content[len(active_prefix):]

            # Return whether the command of the new content is the same as `ctx.command`.
            content_split = content.split()
            accu = []
            matches = False
            for cmd_or_arg, parent in zip_longest(content_split, ctx.command.parents + [ctx.command]):
                if cmd_or_arg is None:
                    # `cmd_or_arg` will only ever be `None` due to `zip_longest` filling the value.
                    # This means that `content_split` is shorter than parents+command, and thus
                    # cannot be the same command (has to be missing at least one level of commands)
                    matches = False
                    break

                accu.append(cmd_or_arg)
                curr_comm = ctx.bot.get_command(' '.join(accu))

                if not curr_comm:
                    continue

                if parent is None:
                    # `parent` will only ever be `None` due to `zip_longest` filling the value.

                    if curr_comm.qualified_name.endswith(cmd_or_arg):
                        # `cmd_or_arg` is a command (not an arg), which
                        # means it's a subcommand of `ctx.command` so not same
                        matches = False
                    else:
                        # `cmd_or_arg` is an arg (not a command), which
                        # means `curr_comm` is as deep as the command goes
                        matches = curr_comm.qualified_name == ctx.command.qualified_name
                    break

                if not curr_comm.qualified_name == parent.qualified_name:
                    # Command doesn't match, but there may be a valid subcommand
                    continue

                if curr_comm.qualified_name == ctx.command.qualified_name:
                    # Currently matches, but we need to ensure that `content_split` doesn't turn into a subcommand
                    matches = True
                    continue

                matches = False

            if matches:
                await ctx.bot.invoke(await ctx.bot.get_context(new_message))
            else:
                await ctx.reply(":warning: You changed the command, so no longer listening for edits.")
