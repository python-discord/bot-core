from collections.abc import Sequence

import discord

from pydis_core.utils.logging import get_logger
from pydis_core.utils.scheduling import create_task

log = get_logger(__name__)


def reaction_check(
    reaction: discord.Reaction,
    user: discord.abc.User,
    *,
    message_id: int,
    allowed_emoji: Sequence[str],
    allowed_users: Sequence[int],
    allowed_roles: Sequence[int] | None = None,
) -> bool:
    """
    Check if a reaction's emoji and author are allowed and the message is `message_id`.

    If the user is not allowed, remove the reaction. Ignore reactions made by the bot.
    If `allow_mods` is True, allow users with moderator roles even if they're not in `allowed_users`.
    """
    right_reaction = (
        not user.bot
        and reaction.message.id == message_id
        and str(reaction.emoji) in allowed_emoji
    )
    if not right_reaction:
        return False

    allowed_roles = allowed_roles or []
    has_sufficient_roles = any(role.id in allowed_roles for role in getattr(user, "roles", []))

    if user.id in allowed_users or has_sufficient_roles:
        log.trace(f"Allowed reaction {reaction} by {user} on {reaction.message.id}.")
        return True

    log.trace(f"Removing reaction {reaction} by {user} on {reaction.message.id}: disallowed user.")
    create_task(
        reaction.message.remove_reaction(reaction.emoji, user),
        suppressed_exceptions=(discord.HTTPException,),
        name=f"remove_reaction-{reaction}-{reaction.message.id}-{user}"
    )
    return False
