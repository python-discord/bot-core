"""Useful helper functions for interactin with :obj:`discord.Member` objects."""
import typing
from collections import abc

import discord

from pydis_core.utils import logging

log = logging.get_logger(__name__)


async def get_or_fetch_member(guild: discord.Guild, member_id: int) -> typing.Optional[discord.Member]:
    """
    Attempt to get a member from cache; on failure fetch from the API.

    Returns:
        The :obj:`discord.Member` or :obj:`None` to indicate the member could not be found.
    """
    if member := guild.get_member(member_id):
        log.trace(f"{member} retrieved from cache.")
        return member
    try:
        member = await guild.fetch_member(member_id)
    except discord.errors.HTTPException as e:
        log.trace(f"Failed to fetch {member_id} from API.")
        if e.status in [400, 404]:
            return None
        raise
    log.trace(f"{member} fetched from API.")
    return member


async def handle_role_change(
    member: discord.Member,
    coro: typing.Callable[[discord.Role], abc.Coroutine],
    role: discord.Role
) -> None:
    """
    Await the given ``coro`` with ``role`` as the sole argument.

    Handle errors that we expect to be raised from
    :obj:`discord.Member.add_roles` and :obj:`discord.Member.remove_roles`.

    Args:
        member: The member that is being modified for logging purposes.
        coro: This is intended to be :obj:`discord.Member.add_roles` or :obj:`discord.Member.remove_roles`.
        role: The role to be passed to ``coro``.
    """
    try:
        await coro(role)
    except discord.NotFound:
        log.error(f"Failed to change role for {member} ({member.id}): member not found")
    except discord.Forbidden:
        log.error(
            f"Forbidden to change role for {member} ({member.id}); "
            f"possibly due to role hierarchy"
        )
    except discord.HTTPException as e:
        log.error(f"Failed to change role for {member} ({member.id}): {e.status} {e.code}")
