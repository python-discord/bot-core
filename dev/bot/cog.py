from discord.ext import commands

from . import Bot


class Cog(commands.Cog):
    """A simple discord.py cog."""

    def __init__(self, _bot: Bot):
        self.bot = _bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Print a message when the client (re)connects."""
        print("Client is ready.")  # noqa: T201

    @commands.command()
    async def reload(self, ctx: commands.Context) -> None:
        """Reload all available cogs."""
        message = await ctx.send(":hourglass_flowing_sand: Reloading")
        for ext in list(self.bot.extensions):
            await self.bot.reload_extension(ext)
        await message.edit(content=":white_check_mark: Done")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Test if the bot is online."""
        await ctx.send("We are live!")


async def setup(_bot: Bot) -> None:
    """Install the cog."""
    await _bot.add_cog(Cog(_bot))
