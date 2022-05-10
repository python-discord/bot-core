from typing import Optional

from botcore.utils.regex import DISCORD_INVITE


def use_regex(s: str) -> Optional[str]:
    """Helper function to run the Regex on a string.

    Return the invite capture group, if the string matches the pattern
        else return None
    """
    result = DISCORD_INVITE.search(s)
    return result if result is None else result.group("invite")


def test_discord_invite_positives():
    """Test the DISCORD_INVITE regex on a set of strings we would expect to capture."""

    assert use_regex("discord.gg/python") == "python"
    assert use_regex("https://discord.gg/python") == "python"
    assert use_regex("discord.com/invite/python") == "python"
    assert use_regex("discordapp.com/invite/python") == "python"
    assert use_regex("discord.me/python") == "python"
    assert use_regex("discord.li/python") == "python"
    assert use_regex("discord.io/python") == "python"
    assert use_regex(".gg/python") == "python"

    assert use_regex("discord.gg/python/but/extra") == "python/but/extra"
    assert use_regex("discord.me/this/isnt/python") == "this/isnt/python"
    assert use_regex(".gg/a/a/a/a/a/a/a/a/a/a/a") == "a/a/a/a/a/a/a/a/a/a/a"
    assert use_regex("discordapp.com/invite/python/snakescord") == "python/snakescord"
    assert use_regex("http://discord.gg/python/%20/notpython") == "python/%20/notpython"
    assert use_regex("discord.gg/python?=ts/notpython") == "python?=ts/notpython"
    assert use_regex("https://discord.gg/python#fragment/notpython") == "python#fragment/notpython"
    assert use_regex("https://discord.gg/python/~/notpython") == "python/~/notpython"

    assert use_regex("https://discord.gg/python with whitespace") == "python"
    assert use_regex(" https://discord.gg/python ") == "python"


def test_discord_invite_negatives():
    """Test the DISCORD_INVITE regex on a set of strings we would expect to not capture."""

    assert use_regex("another string") is None
    assert use_regex("https://pythondiscord.com") is None
    assert use_regex("https://discord.com") is None
    assert use_regex("https://discord.gg") is None
    assert use_regex("https://discord.gg/ python") is None
