"""Contains all common monkey patches, used to alter discord to fit our needs."""

import logging
import typing
from datetime import datetime, timedelta
from functools import partial, partialmethod

from discord import Forbidden, http
from discord.ext import commands

log = logging.getLogger(__name__)


class _Command(commands.Command):
    """
    A :obj:`discord.ext.commands.Command` subclass which supports root aliases.

    A ``root_aliases`` keyword argument is added, which is a sequence of alias names that will act as
    top-level commands rather than being aliases of the command's group. It's stored as an attribute
    also named ``root_aliases``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_aliases = kwargs.get("root_aliases", [])

        if not isinstance(self.root_aliases, (list, tuple)):
            raise TypeError("Root aliases of a command must be a list or a tuple of strings.")


class _Group(commands.Group, _Command):
    """
    A :obj:`discord.ext.commands.Group` subclass which supports root aliases.

    A ``root_aliases`` keyword argument is added, which is a sequence of alias names that will act as
    top-level groups rather than being aliases of the command's group. It's stored as an attribute
    also named ``root_aliases``.
    """


def _patch_typing() -> None:
    """
    Sometimes Discord turns off typing events by throwing 403s.

    Handle those issues by patching discord's internal ``send_typing`` method so it ignores 403s in general.
    """
    log.debug("Patching send_typing, which should fix things breaking when Discord disables typing events. Stay safe!")

    original = http.HTTPClient.send_typing
    last_403: typing.Optional[datetime] = None

    async def honeybadger_type(self: http.HTTPClient, channel_id: int) -> None:
        nonlocal last_403
        if last_403 and (datetime.utcnow() - last_403) < timedelta(minutes=5):
            log.warning("Not sending typing event, we got a 403 less than 5 minutes ago.")
            return
        try:
            await original(self, channel_id)
        except Forbidden:
            last_403 = datetime.utcnow()
            log.warning("Got a 403 from typing event!")

    http.HTTPClient.send_typing = honeybadger_type


def _apply_monkey_patches() -> None:
    """This is surfaced directly in pydis_core.utils.apply_monkey_patches()."""
    commands.command = partial(commands.command, cls=_Command)
    commands.GroupMixin.command = partialmethod(commands.GroupMixin.command, cls=_Command)

    commands.group = partial(commands.group, cls=_Group)
    commands.GroupMixin.group = partialmethod(commands.GroupMixin.group, cls=_Group)
    _patch_typing()
