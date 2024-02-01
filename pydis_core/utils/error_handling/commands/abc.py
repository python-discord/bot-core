from abc import ABC, abstractmethod
from typing import NoReturn

from discord import Interaction
from discord.ext.commands import Context


class AbstractCommandErrorHandler(ABC):
    """An abstract command error handler."""

    @abstractmethod
    async def should_handle_error(self, error: Exception) -> bool:
        """A predicate that determines whether the error should be handled."""
        raise NotImplementedError

    @abstractmethod
    async def handle_app_command_error(self, interaction: Interaction, error: Exception) -> NoReturn:
        """Handle error raised in the context of app commands."""
        raise NotImplementedError

    @abstractmethod
    async def handle_text_command_error(self, context: Context, error: Exception) -> NoReturn:
        """Handle error raised in the context of text commands."""
        raise NotImplementedError
