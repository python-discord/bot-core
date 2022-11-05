import contextlib
from typing import Optional, Sequence

from discord import ButtonStyle, Interaction, Message, NotFound, ui

from pydis_core.utils.logging import get_logger

log = get_logger(__name__)


class ViewWithUserAndRoleCheck(ui.View):
    """
    A view that allows the original invoker and moderators to interact with it.

    Args:
        allowed_users: A sequence of user's ids who are allowed to interact with the view.
        allowed_roles: A sequence of role ids that are allowed to interact with the view.
        timeout: Timeout in seconds from last interaction with the UI before no longer accepting input.
            If ``None`` then there is no timeout.
        message: The message to remove the view from on timeout. This can also be set with
            ``view.message = await ctx.send( ... )``` , or similar, after the view is instantiated.
    """

    def __init__(
        self,
        *,
        allowed_users: Sequence[int],
        allowed_roles: Sequence[int],
        timeout: Optional[float] = 180.0,
        message: Optional[Message] = None
    ) -> None:
        super().__init__(timeout=timeout)
        self.allowed_users = allowed_users
        self.allowed_roles = allowed_roles
        self.message = message

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Ensure the user clicking the button is the view invoker, or a moderator.

        Args:
            interaction: The interaction that occurred.
        """
        if interaction.user.id in self.allowed_users:
            log.trace(
                "Allowed interaction by %s (%d) on %d as they are an allowed user.",
                interaction.user,
                interaction.user.id,
                interaction.message.id,
            )
            return True

        if any(role.id in self.allowed_roles for role in getattr(interaction.user, "roles", [])):
            log.trace(
                "Allowed interaction by %s (%d)on %d as they have an allowed role.",
                interaction.user,
                interaction.user.id,
                interaction.message.id,
            )
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        """Remove the view from ``self.message`` if set."""
        if self.message:
            with contextlib.suppress(NotFound):
                # Cover the case where this message has already been deleted by external means
                await self.message.edit(view=None)


class DeleteMessageButton(ui.Button):
    """
    A button that can be added to a view to delete the message containing the view on click.

    This button itself carries out no interaction checks, these should be done by the parent view.

    See :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck` for a view that implements basic checks.

    Args:
        style (:literal-url:`ButtonStyle <https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.ButtonStyle>`):
            The style of the button, set to ``ButtonStyle.secondary`` if not specified.
        label: The label of the button, set to "Delete" if not specified.
    """  # noqa: E501

    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str = "Delete",
        **kwargs
    ):
        super().__init__(style=style, label=label, **kwargs)

    async def callback(self, interaction: Interaction) -> None:
        """Delete the original message on button click."""
        await interaction.message.delete()
