import asyncio
import os

import aiohttp
import discord
import dotenv
from discord.ext import commands

import pydis_core

from . import Bot

dotenv.load_dotenv()
pydis_core.utils.apply_monkey_patches()

roles = os.getenv("ALLOWED_ROLES")
roles = [int(role) for role in roles.split(",")] if roles else []

bot = Bot(
    guild_id=int(os.getenv("GUILD_ID")),
    http_session=None,  # type: ignore We need to instantiate the session in an async context
    allowed_roles=roles,
    command_prefix=commands.when_mentioned_or(os.getenv("PREFIX", "!")),
    intents=discord.Intents.all(),
    description="Bot-core test bot.",
)


async def main() -> None:
    """Run the bot."""
    bot.http_session = aiohttp.ClientSession()
    async with bot:
        await bot.start(os.getenv("BOT_TOKEN"))

if os.getenv("IN_CI", "").lower() != "true":
    asyncio.run(main())
