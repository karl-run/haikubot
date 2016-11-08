import unittest

from bot.commands.commands import Commands


class CommandsTest(unittest.TestCase):
    def test_values(self):
        values = Commands.values()
        good = ['add mod', 'remove mod', 'list mod',
                'show last', 'show', 'show from', 'stats top']
        self.assertEqual(good, values)
