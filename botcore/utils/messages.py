import asyncio
import random
import re
from functools import partial
from io import BytesIO
from typing import Callable, Sequence

import discord
from discord.ext import commands

from botcore.utils import scheduling
from botcore.utils.logging import get_logger


log = get_logger(__name__)


def reaction_check(
    reaction: discord.Reaction,
    user: discord.abc.User,
    *,
    message_id: int,
    allowed_emojis: Sequence[str],
    allowed_users: Sequence[int],
    allowed_roles: Sequence[int],
) -> bool:
    """
    Checks if a reaction's emoji and author are allowed.

    A reaction's emoji is allowed when it's not by a bot, is on `message_id`, and in `allowed_emojis`.
    A user is allowed when their id is in `allowed_users`, or they have a role that's in `allowed_roles`.

    If the user is not allowed, removes the reaction.
    """
    right_reaction = (
        not user.bot
        and reaction.message.id == message_id
        and str(reaction.emoji) in allowed_emojis
    )
    if not right_reaction:
        return False

    if user.id in allowed_users or any(role.id in allowed_roles for role in getattr(user, "roles", [])):
        log.trace(f"Allowed reaction {reaction} by {user} on {reaction.message.id}.")
        return True
    else:
        log.trace(f"Removing reaction {reaction} by {user} on {reaction.message.id}: disallowed user.")
        scheduling.create_task(
            reaction.message.remove_reaction(reaction.emoji, user),
            suppressed_exceptions=(discord.HTTPException,),
            name=f"remove_reaction-{reaction}-{reaction.message.id}-{user}"
        )
        return False


async def wait_for_deletion(
    bot: commands.Bot,
    message: discord.Message,
    *,
    allowed_users: Sequence[int],
    allowed_roles: Sequence[int],
    deletion_emojis: Sequence[str] = ("<:trashcan:675729438528503910>",),
    timeout: float = 60 * 5,
    attach_emojis: bool = True,
) -> None:
    """
    Waits for an allowed user to react with one of the `deletion_emojis` within `timeout` seconds to delete `message`.

    A user is defined as allowed if their id is in `allowed_users`, or they have a role that's in `allowed_roles`.

    If `timeout` expires then reactions are cleared to indicate the option to delete has expired.

    An `attach_emojis` bool may be provided to determine whether to attach the given `deletion_emojis` to the `message`.
    """
    if message.guild is None:
        raise ValueError("Message must be sent on a guild")

    if attach_emojis:
        for emoji in deletion_emojis:
            try:
                await message.add_reaction(emoji)
            except discord.NotFound:
                log.trace(f"Aborting wait_for_deletion: message {message.id} deleted prematurely.")
                return

    check = partial(
        reaction_check,
        message_id=message.id,
        allowed_emoji=deletion_emojis,
        allowed_users=allowed_users,
        allowed_roles=allowed_roles,
    )

    try:
        try:
            await bot.wait_for('reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.clear_reactions()
        else:
            await message.delete()
    except discord.NotFound:
        log.trace(f"wait_for_deletion: message {message.id} deleted prematurely.")


async def send_attachments(
    message: discord.Message,
    destination: discord.TextChannel | discord.Webhook,
    link_large: bool = True,
    use_cached: bool = False,
    **kwargs
) -> list[str]:
    """
    Re-upload the message's attachments to the destination and return a list of their new URLs.

    Each attachment is sent as a separate message to more easily comply with the request/file size
    limit. If link_large is True, attachments which are too large are instead grouped into a single
    embed which links to them. Extra kwargs will be passed to send() when sending the attachment.
    """
    webhook_send_kwargs = {
        'username': message.author.display_name,
        'avatar_url': message.author.display_avatar.url,
    }
    webhook_send_kwargs.update(kwargs)
    webhook_send_kwargs['username'] = sub_clyde(webhook_send_kwargs['username'])

    large = []
    urls = []
    for attachment in message.attachments:
        failure_msg = (
            f"Failed to re-upload attachment {attachment.filename} from message {message.id}"
        )

        try:
            # Allow 512 bytes of leeway for the rest of the request.
            # This should avoid most files that are too large,
            # but some may get through hence the try-catch.
            if attachment.size <= destination.guild.filesize_limit - 512:
                with BytesIO() as file:
                    await attachment.save(file, use_cached=use_cached)
                    attachment_file = discord.File(file, filename=attachment.filename)

                    if isinstance(destination, discord.TextChannel):
                        msg = await destination.send(file=attachment_file, **kwargs)
                        urls.append(msg.attachments[0].url)
                    else:
                        await destination.send(file=attachment_file, **webhook_send_kwargs)
            elif link_large:
                large.append(attachment)
            else:
                log.info(f"{failure_msg} because it's too large.")
        except discord.HTTPException as e:
            if link_large and e.status == 413:
                large.append(attachment)
            else:
                log.warning(f"{failure_msg} with status {e.status}.", exc_info=e)

    if link_large and large:
        desc = "\n".join(f"[{attachment.filename}]({attachment.url})" for attachment in large)
        embed = discord.Embed(description=desc)
        embed.set_footer(text="Attachments exceed upload size limit.")

        if isinstance(destination, discord.TextChannel):
            await destination.send(embed=embed, **kwargs)
        else:
            await destination.send(embed=embed, **webhook_send_kwargs)

    return urls


async def count_unique_users_reaction(
    message: discord.Message,
    reaction_predicate: Callable[[discord.Reaction], bool] = lambda _: True,
    user_predicate: Callable[[discord.User], bool] = lambda _: True,
    count_bots: bool = True
) -> int:
    """
    Count the amount of unique users who reacted to the message.

    A reaction_predicate function can be passed to check if this reaction should be counted,
    another user_predicate to check if the user should also be counted along with a count_bot flag.
    """
    unique_users = set()

    for reaction in message.reactions:
        if reaction_predicate(reaction):
            async for user in reaction.users():
                if (count_bots or not user.bot) and user_predicate(user):
                    unique_users.add(user.id)

    return len(unique_users)


async def pin_no_system_message(message: discord.Message) -> bool:
    """Pin the given message, wait a couple of seconds and try to delete the system message."""
    await message.pin()

    # Make sure that we give it enough time to deliver the message
    await asyncio.sleep(2)
    # Search for the system message in the last 10 messages
    async for historical_message in message.channel.history(limit=10):
        if historical_message.type == discord.MessageType.pins_add:
            await historical_message.delete()
            return True

    return False


async def send_denial(ctx: commands.Context, reason: str, *, negative_replies: Sequence[str]) -> discord.Message:
    """Send an embed denying the user with the given reason."""
    embed = discord.Embed()
    embed.colour = discord.Colour.red()
    embed.title = random.choice(negative_replies)
    embed.description = reason

    return await ctx.send(embed=embed)


def format_user(user: discord.abc.User) -> str:
    """Return a string for `user` which has their mention and ID."""
    return f"{user.mention} (`{user.id}`)"


def sub_clyde(username: str | None) -> str | None:
    """
    Replace "e"/"E" in any "clyde" in `username` with a Cyrillic "е"/"E" and return the new string.

    Discord disallows "clyde" anywhere in the username for webhooks. It will return a 400.
    Return None only if `username` is None.
    """
    def replace_e(match: re.Match) -> str:
        char = "е" if match[2] == "e" else "Е"
        return match[1] + char

    if username:
        return re.sub(r"(clyd)(e)", replace_e, username, flags=re.I)
    else:
        return username  # Empty string or None


async def get_discord_message(ctx: commands.Context, text: str) -> discord.Message | str:
    """
    Attempts to convert a given `text` to a discord Message object and return it.

    Conversion will succeed if given a discord Message ID or link.
    Returns `text` if the conversion fails.
    """
    try:
        text = await commands.MessageConverter().convert(ctx, text)
    except commands.BadArgument:
        pass

    return text


async def get_text_and_embed(ctx: commands.Context, text: str) -> tuple[str, discord.Embed | None]:
    """
    Attempts to extract the text and embed from a possible link to a discord Message.

    Does not retrieve the text and embed from the Message if it is in a channel the user does
    not have read permissions in.

    Returns a tuple of:
        str: If `text` is a valid discord Message, the contents of the message, else `text`.
        Embed | None: The embed if found in the valid Message, else `None`
    """
    embed: discord.Embed | None = None

    msg = await get_discord_message(ctx, text)
    # Ensure the user has read permissions for the channel the message is in
    if isinstance(msg, discord.Message):
        permissions = msg.channel.permissions_for(ctx.author)
        if permissions.read_messages:
            text = msg.clean_content
            # Take first embed because we can't send multiple embeds
            if msg.embeds:
                embed = msg.embeds[0]

    return text, embed


def convert_embed(func: Callable[[str, ], str], embed: discord.Embed) -> discord.Embed:
    """
    Converts the text in an embed using a given conversion function, then return the embed.

    Only modifies the following fields: title, description, footer, fields
    """
    embed_dict = embed.to_dict()

    embed_dict["title"] = func(embed_dict.get("title", ""))
    embed_dict["description"] = func(embed_dict.get("description", ""))

    if "footer" in embed_dict:
        embed_dict["footer"]["text"] = func(embed_dict["footer"].get("text", ""))

    if "fields" in embed_dict:
        for field in embed_dict["fields"]:
            field["name"] = func(field.get("name", ""))
            field["value"] = func(field.get("value", ""))

    return discord.Embed.from_dict(embed_dict)
