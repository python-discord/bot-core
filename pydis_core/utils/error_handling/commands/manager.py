from collections.abc import Callable
from typing import NoReturn

from discord import Interaction
from discord.ext.commands import Context

from pydis_core.utils.error_handling.commands import AbstractCommandErrorHandler
from pydis_core.utils.logging import get_logger

log = get_logger(__name__)


class CommandErrorManager:
    """A class that registers error handlers and handles all command related errors."""

    def __init__(self, default: AbstractCommandErrorHandler):
        self._handlers = []
        self._registered_handlers = set()
        self._default = default

    async def handle_error(
        self,
        error: Exception,
        context_or_interaction: Context | Interaction
    ) -> None:
        """
        Handle a Discord exception.

        Iterate through available handlers by registration order, and choose the first one capable of handling
        the error as determined by `should_handle_error`; there is no priority system.
        """
        error = getattr(error, "original", error)
        for handler in self._handlers + [self._default]:
            if await handler.should_handle_error(error):
                callback = self._get_callback(handler, context_or_interaction)
                await callback(context_or_interaction, error)
                break

    def register_handler(self, handler: AbstractCommandErrorHandler) -> None:
        """Register a command error handler."""
        handler_name = type(handler).__name__
        if handler_name in self._registered_handlers:
            log.info(f"Skipping registration of command error handler {handler_name!r} as it's already registered.")
            return

        self._handlers.append(handler)
        self._registered_handlers.add(handler_name)

    @staticmethod
    def _get_callback(
        handler: AbstractCommandErrorHandler,
        context_or_interaction: Context | Interaction
    ) -> Callable[[Context, Exception], NoReturn] | Callable[[Interaction, Exception], NoReturn] | None:
        """Get the handling callback that will be used."""
        if isinstance(context_or_interaction, Context):
            return handler.handle_text_command_error
        if isinstance(context_or_interaction, Interaction):
            return handler.handle_app_command_error
        raise ValueError(f"Expected Context or Interaction, got {type(context_or_interaction).__name__}")
