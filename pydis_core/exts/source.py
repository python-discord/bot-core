"""Pre-built cog to display source code links for commands and cogs."""
import enum
import inspect
from importlib import metadata
from pathlib import Path
from typing import NamedTuple, TYPE_CHECKING

from discord import Embed
from discord.ext import commands
from discord.utils import escape_markdown

if TYPE_CHECKING:
    from pydis_core import BotBase as Bot


GITHUB_AVATAR = "https://avatars1.githubusercontent.com/u/9919"
BOT_CORE_REPO = "https://github.com/python-discord/bot-core"

class _TagIdentifierStub(NamedTuple):
    """A minmally functioning stub representing a tag identifier."""

    group: str | None
    name: str

    @classmethod
    def from_string(cls, string: str) -> "_TagIdentifierStub":
        """Create a TagIdentifierStub from a string."""
        split_string = string.split(" ", maxsplit=2)
        if len(split_string) == 1:
            return cls(None, split_string[0])
        return cls(split_string[0], split_string[1])


class _SourceType(enum.StrEnum):
    """The types of source objects recognized by the source command."""

    help_command = enum.auto()
    text_command = enum.auto()
    core_command = enum.auto()
    cog = enum.auto()
    core_cog = enum.auto()
    tag = enum.auto()
    extension_not_loaded = enum.auto()


class SourceCode(commands.Cog, description="Displays information about the bot's source code."):
    """
    Pre-built cog to display source code links for commands and cogs (and if applicable, tags).

    To use this cog, instantiate it with the bot instance and the base GitHub repository URL.

    Args:
        bot (:obj:`pydis_core.BotBase`): The bot instance.
        github_repo: The base URL to the GitHub repository (e.g. `https://github.com/python-discord/bot`).
    """

    def __init__(self, bot: "Bot", github_repo: str) -> None:
        self.bot = bot
        self.github_repo = github_repo

    @commands.command(name="source", aliases=("src",))
    async def source_command(
        self,
        ctx: "commands.Context[Bot]",
        *,
        source_item: str | None = None,
    ) -> None:
        """Display information and a GitHub link to the source code of a command, tag, or cog."""
        if not source_item:
            embed = Embed(title=f"{self.bot.user.name}'s GitHub Repository")
            embed.add_field(name="Repository", value=f"[Go to GitHub]({self.github_repo})")
            embed.set_thumbnail(url=GITHUB_AVATAR)
            await ctx.send(embed=embed)
            return

        obj, source_type = await self._get_source_object(ctx, source_item)
        embed = await self._build_embed(obj, source_type)
        await ctx.send(embed=embed)

    @staticmethod
    async def _get_source_object(ctx: "commands.Context[Bot]", argument: str) -> tuple[object, _SourceType]:
        """Convert argument into the source object and source type."""
        if argument.lower() == "help":
            return ctx.bot.help_command, _SourceType.help_command

        cog = ctx.bot.get_cog(argument)
        if cog:
            if cog.__module__.startswith("pydis_core.exts"):
                return cog, _SourceType.core_cog
            return cog, _SourceType.cog

        cmd = ctx.bot.get_command(argument)
        if cmd:
            if cmd.module.startswith("pydis_core.exts"):
                return cmd, _SourceType.core_command
            return cmd, _SourceType.text_command

        tags_cog = ctx.bot.get_cog("Tags")
        show_tag = True

        if not tags_cog:
            show_tag = False
        else:
            identifier = _TagIdentifierStub.from_string(argument.lower())
            if identifier in tags_cog.tags:
                return identifier, _SourceType.tag

        escaped_arg = escape_markdown(argument)

        raise commands.BadArgument(
            f"Unable to convert '{escaped_arg}' to valid command{', tag,' if show_tag else ''} or Cog."
        )

    def _get_source_link(self, source_item: object, source_type: _SourceType) -> tuple[str, str, int | None]:
        """
        Build GitHub link of source item, return this link, file location and first line number.

        Raise BadArgument if `source_item` is a dynamically-created object (e.g. via internal eval).
        """
        if source_type == _SourceType.text_command or source_type == _SourceType.core_command:
            source_item = inspect.unwrap(source_item.callback)
            src = source_item.__code__
            filename = src.co_filename
        elif source_type == _SourceType.tag:
            tags_cog = self.bot.get_cog("Tags")
            filename = tags_cog.tags[source_item].file_path
        else:
            src = type(source_item)
            try:
                filename = inspect.getsourcefile(src)
            except TypeError:
                raise commands.BadArgument("Cannot get source for a dynamically-created object.")

        if source_type != _SourceType.tag:
            try:
                lines, first_line_no = inspect.getsourcelines(src)
            except OSError:
                raise commands.BadArgument("Cannot get source for a dynamically-created object.")

            lines_extension = f"#L{first_line_no}-L{first_line_no+len(lines)-1}"
        else:
            first_line_no = None
            lines_extension = ""

        # Handle tag file location differently than others to avoid errors in some cases
        if not first_line_no:
            file_location = Path(filename)
        elif source_type == _SourceType.core_command:
            package_location = metadata.distribution("pydis_core").locate_file("") / "pydis_core"
            internal_location = Path(filename).relative_to(package_location).as_posix()
            file_location = "pydis_core/" + internal_location
        elif source_type == _SourceType.core_cog:
            package_location = metadata.distribution("pydis_core").locate_file("") / "pydis_core" / "exts"
            internal_location = Path(filename).relative_to(package_location).as_posix()
            file_location = "pydis_core/exts/" + internal_location
        else:
            file_location = Path(filename).relative_to(Path.cwd()).as_posix()

        repo = self.github_repo if source_type != _SourceType.core_command else BOT_CORE_REPO

        if source_type == _SourceType.core_command or source_type == _SourceType.core_cog:
            version = f"v{metadata.version('pydis_core')}"
        else:
            version = "main"

        url = f"{repo}/blob/{version}/{file_location}{lines_extension}"

        return url, file_location, first_line_no or None

    async def _build_embed(self, source_object: object, source_type: _SourceType) -> Embed | None:
        """Build embed based on source object."""
        url, location, first_line = self._get_source_link(source_object, source_type)

        if source_type == _SourceType.help_command:
            title = "Help Command"
            description = source_object.__doc__.splitlines()[1]
        elif source_type == _SourceType.text_command:
            description = source_object.short_doc
            title = f"Command: {source_object.qualified_name}"
        elif source_type == _SourceType.core_command:
            description = source_object.short_doc
            title = f"Core Command: {source_object.qualified_name}"
        elif source_type == _SourceType.core_cog:
            title = f"Core Cog: {source_object.qualified_name}"
            description = source_object.description.splitlines()[0]
        elif source_type == _SourceType.tag:
            title = f"Tag: {source_object}"
            description = ""
        else:
            title = f"Cog: {source_object.qualified_name}"
            description = source_object.description.splitlines()[0]

        embed = Embed(title=title, description=description)
        embed.add_field(name="Source Code", value=f"[Go to GitHub]({url})")
        line_text = f":{first_line}" if first_line else ""
        embed.set_footer(text=f"{location}{line_text}", icon_url=GITHUB_AVATAR)

        return embed
