"""
Loads bot configuration from environment variables and `.env` files.

By default, the values defined in the classes are used, these can be overridden by an env var with the same name.

`.env` and `.env.server` files are used to populate env vars, if present.
"""
from pydantic import BaseSettings


class EnvConfig(BaseSettings):
    """Our default configuration for models that should load from .env files."""

    class Config:
        """Specify what .env files to load, and how to load them."""

        env_file = ".env.server",
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


class _PaginationEmojis(EnvConfig):

    first: str = "\u23EE"
    left: str = "\u2B05"
    right: str = "\u27A1"
    last: str = "\u23ED"
    delete: str = "<:trashcan:637136429717389331>"
