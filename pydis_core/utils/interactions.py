from collections.abc import Sequence
from typing import Literal

from discord import ButtonStyle, HTTPException, Interaction, Member, Message, NotFound, User, ui

from pydis_core.utils.logging import get_logger
from pydis_core.utils.scheduling import create_task

log = get_logger(__name__)


def user_has_access(
    user: User | Member,
    *,
    allowed_users: Sequence[int] = (),
    allowed_roles: Sequence[int] = (),
) -> bool:
    """
    Return whether the user is in the allowed_users list, or has a role from allowed_roles.

    Args:
        user: The user to check
        allowed_users: A sequence of user ids that are allowed access
        allowed_roles: A sequence of role ids that are allowed access
    """
    if user.id in allowed_users or any(role.id in allowed_roles for role in getattr(user, "roles", [])):
        return True
    return False


async def _handle_modify_message(message: Message, action: Literal["edit", "delete"]) -> None:
    """Remove the view from, or delete the given message depending on the specified action."""
    try:
        if action == "edit":
            await message.edit(view=None)
        elif action == "delete":
            await message.delete()
    except HTTPException as e:
        # Cover the case where this message has been deleted by external means,
        # or the message is now in an archived/locked thread.
        if e.code == 50083:
            log.debug(f"Could not {action} message {message.id} due to it being in an archived thread.")
        elif isinstance(e, NotFound):
            log.info(f"Could not find message {message.id} when attempting to {action} it.")
        else:
            log.exception(f"Could not {action} message {message.id} due to Discord HTTP error:")


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
        timeout: float | None = 180.0,
        message: Message | None = None
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
        if user_has_access(
            interaction.user,
            allowed_users=self.allowed_users,
            allowed_roles=self.allowed_roles,
        ):
            log.trace(
                "Allowed interaction by %s (%d) on %d as they are an allowed user or have an allowed role.",
                interaction.user,
                interaction.user.id,
                interaction.message.id,
            )
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral=True)
        return False

    def stop(self) -> None:
        """Stop listening for interactions, and remove the view from ``self.message`` if set."""
        super().stop()
        if self.message:
            create_task(_handle_modify_message(self.message, "edit"))

    async def on_timeout(self) -> None:
        """Remove the view from ``self.message`` if set."""
        if self.message:
            await _handle_modify_message(self.message, "edit")


class DeleteMessageButton(ui.Button):
    """
    A button that can be added to a view to delete the message containing the view on click.

    This button itself carries out no interaction checks, these should be done by the parent view.

    See :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck` for a view that implements basic checks.

    Args:
        style (:literal-url:`ButtonStyle <https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.ButtonStyle>`):
            The style of the button, set to ``ButtonStyle.secondary`` if not specified.
        label: The label of the button, set to "Delete" if not specified.
    """

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
        await _handle_modify_message(interaction.message, "delete")
