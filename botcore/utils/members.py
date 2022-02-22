"""Useful helper functions for interactin with :obj:`disnake.Member` objects."""

import typing

import disnake

from botcore.utils import logging

log = logging.get_logger(__name__)


async def get_or_fetch_member(guild: disnake.Guild, member_id: int) -> typing.Optional[disnake.Member]:
    """
    Attempt to get a member from cache; on failure fetch from the API.

    Returns:
        The :obj:`disnake.Member` or :obj:`None` to indicate the member could not be found.
    """
    if member := guild.get_member(member_id):
        log.trace(f"{member} retrieved from cache.")
    else:
        try:
            member = await guild.fetch_member(member_id)
        except disnake.errors.NotFound:
            log.trace(f"Failed to fetch {member_id} from API.")
            return None
        log.trace(f"{member} fetched from API.")
    return member


async def handle_role_change(
    member: disnake.Member,
    coro: typing.Callable[..., typing.Coroutine],
    role: disnake.Role
) -> None:
    """
    Await the given ``coro`` with ``member`` as the sole argument.

    Handle errors that we expect to be raised from
    :obj:`disnake.Member.add_roles` and :obj:`disnake.Member.remove_roles`.

    Args:
        member: The member to pass to ``coro``.
        coro: This is intended to be :obj:`disnake.Member.add_roles` or :obj:`disnake.Member.remove_roles`.
    """
    try:
        await coro(role)
    except disnake.NotFound:
        log.error(f"Failed to change role for {member} ({member.id}): member not found")
    except disnake.Forbidden:
        log.error(
            f"Forbidden to change role for {member} ({member.id}); "
            f"possibly due to role hierarchy"
        )
    except disnake.HTTPException as e:
        log.error(f"Failed to change role for {member} ({member.id}): {e.status} {e.code}")
