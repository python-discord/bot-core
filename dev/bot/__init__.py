import asyncio
import logging
import os
import sys

import pydis_core

if os.name == "nt":
    # Change the event loop policy on Windows to avoid exceptions on exit
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Some basic logging to get existing loggers to show
logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("discord").setLevel(logging.ERROR)


class Bot(pydis_core.BotBase):
    """Sample Bot implementation."""

    async def setup_hook(self) -> None:
        """Load extensions on startup."""
        await super().setup_hook()
        await self.load_extensions(sys.modules[__name__])
