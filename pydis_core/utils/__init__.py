"""Useful utilities and tools for Discord bot development."""

import pydis_core.utils.error_handling.commands as command_error_handling_module
import pydis_core.utils.error_handling.commands.abc as error_handling_abstractions
import pydis_core.utils.error_handling.commands.manager as command_error_manager
from pydis_core.utils import (
    _monkey_patches,
    caching,
    channel,
    checks,
    commands,
    cooldown,
    error_handling,
    function,
    interactions,
    lock,
    logging,
    members,
    messages,
    pagination,
    paste_service,
    regex,
    scheduling,
)
from pydis_core.utils._extensions import unqualify


def apply_monkey_patches() -> None:
    """
    Applies all common monkey patches for our bots.

    Patches :obj:`discord.ext.commands.Command` and :obj:`discord.ext.commands.Group` to support root aliases.
        A ``root_aliases`` keyword argument is added to these two objects, which is a sequence of alias names
        that will act as top-level groups rather than being aliases of the command's group.

        It's stored as an attribute also named ``root_aliases``

    Patches discord's internal ``send_typing`` method so that it ignores 403 errors from Discord.
        When under heavy load Discord has added a CloudFlare worker to this route, which causes 403 errors to be thrown.
    """
    _monkey_patches._apply_monkey_patches()  # noqa: SLF001


__all__ = [
    apply_monkey_patches,
    caching,
    channel,
    checks,
    commands,
    command_error_handling_module,
    error_handling_abstractions,
    command_error_manager,
    cooldown,
    error_handling,
    function,
    interactions,
    lock,
    logging,
    members,
    messages,
    pagination,
    paste_service,
    regex,
    scheduling,
    unqualify,
]

__all__ = [module.__name__ for module in __all__]
