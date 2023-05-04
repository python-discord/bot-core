import unittest
from typing import Optional

from pydis_core.utils.regex import DISCORD_INVITE


def match_regex(s: str) -> Optional[str]:
    """Helper function to run re.match on a string.

    Return the invite capture group, if the string matches the pattern
        else return None
    """
    result = DISCORD_INVITE.match(s)
    return result if result is None else result.group("invite")


def search_regex(s: str) -> Optional[str]:
    """Helper function to run re.search on a string.

    Return the invite capture group, if the string matches the pattern
        else return None
    """
    result = DISCORD_INVITE.search(s)
    return result if result is None else result.group("invite")


class UtilsRegexTests(unittest.TestCase):

    def test_discord_invite_positives(self):
        """Test the DISCORD_INVITE regex on a set of strings we would expect to capture."""

        self.assertEqual(match_regex("discord.gg/python"), "python")
        self.assertEqual(match_regex("https://discord.gg/python"), "python")
        self.assertEqual(match_regex("https://www.discord.gg/python"), "python")
        self.assertEqual(match_regex("discord.com/invite/python"), "python")
        self.assertEqual(match_regex("www.discord.com/invite/python"), "python")
        self.assertEqual(match_regex("discordapp.com/invite/python"), "python")
        self.assertEqual(match_regex("discord.me/python"), "python")
        self.assertEqual(match_regex("discord.li/python"), "python")
        self.assertEqual(match_regex("discord.io/python"), "python")
        self.assertEqual(match_regex(".gg/python"), "python")

        self.assertEqual(match_regex("discord.gg/python/but/extra"), "python/but/extra")
        self.assertEqual(match_regex("discord.me/this/isnt/python"), "this/isnt/python")
        self.assertEqual(match_regex(".gg/a/a/a/a/a/a/a/a/a/a/a"), "a/a/a/a/a/a/a/a/a/a/a")
        self.assertEqual(match_regex("discordapp.com/invite/python/snakescord"), "python/snakescord")
        self.assertEqual(match_regex("http://discord.gg/python/%20/notpython"), "python/%20/notpython")
        self.assertEqual(match_regex("discord.gg/python?=ts/notpython"), "python?=ts/notpython")
        self.assertEqual(match_regex("https://discord.gg/python#fragment/notpython"), "python#fragment/notpython")
        self.assertEqual(match_regex("https://discord.gg/python/~/notpython"), "python/~/notpython")

        self.assertEqual(search_regex("https://discord.gg/python with whitespace"), "python")
        self.assertEqual(search_regex(" https://discord.gg/python "), "python")

    def test_discord_invite_negatives(self):
        """Test the DISCORD_INVITE regex on a set of strings we would expect to not capture."""

        self.assertEqual(match_regex("another string"), None)
        self.assertEqual(match_regex("https://pythondiscord.com"), None)
        self.assertEqual(match_regex("https://discord.com"), None)
        self.assertEqual(match_regex("https://discord.gg"), None)
        self.assertEqual(match_regex("https://discord.gg/ python"), None)

        self.assertEqual(search_regex("https://discord.com with whitespace"), None)
        self.assertEqual(search_regex(" https://discord.com "), None)
