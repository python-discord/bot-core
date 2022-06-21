import unittest
from unittest.mock import patch

from botcore.utils.cooldown import _CommandCooldownManager, _create_argument_tuple


class CommandCooldownManagerTests(unittest.IsolatedAsyncioTestCase):
    test_call_args = (
        _create_argument_tuple(0),
        _create_argument_tuple(a=0),
        _create_argument_tuple([]),
        _create_argument_tuple(a=[]),
        _create_argument_tuple(1, 2, 3, a=4, b=5, c=6),
        _create_argument_tuple([1], [2], [3], a=[4], b=[5], c=[6]),
        _create_argument_tuple([1], 2, [3], a=4, b=[5], c=6),
    )

    async def asyncSetUp(self):
        self.cooldown_manager = _CommandCooldownManager(cooldown_duration=5)

    def test_no_cooldown_on_unset(self):
        for call_args in self.test_call_args:
            with self.subTest(arguments_tuple=call_args, channel=0):
                self.assertFalse(self.cooldown_manager.is_on_cooldown(0, call_args))

        for call_args in self.test_call_args:
            with self.subTest(arguments_tuple=call_args, channel=1):
                self.assertFalse(self.cooldown_manager.is_on_cooldown(1, call_args))

    @patch("time.monotonic")
    def test_cooldown_is_set(self, monotonic):
        monotonic.side_effect = lambda: 0
        for call_args in self.test_call_args:
            with self.subTest(arguments_tuple=call_args):
                self.cooldown_manager.set_cooldown(0, call_args)
                self.assertTrue(self.cooldown_manager.is_on_cooldown(0, call_args))

    @patch("time.monotonic")
    def test_cooldown_expires(self, monotonic):
        for call_args in self.test_call_args:
            monotonic.side_effect = (0, 1000)
            with self.subTest(arguments_tuple=call_args):
                self.cooldown_manager.set_cooldown(0, call_args)
                self.assertFalse(self.cooldown_manager.is_on_cooldown(0, call_args))

    def test_keywords_and_tuples_differentiated(self):
        self.cooldown_manager.set_cooldown(0, _create_argument_tuple(("a", 0)))
        self.assertFalse(self.cooldown_manager.is_on_cooldown(0, _create_argument_tuple(a=0)))
        self.assertTrue(self.cooldown_manager.is_on_cooldown(0, _create_argument_tuple(("a", 0))))
