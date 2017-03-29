import unittest

from haikubot.commands.commands import Commands


class CommandsTest(unittest.TestCase):
    def test_values(self):
        values = Commands.values()
        good = ['add mod', 'remove mod', 'list mod', 'show last', 'show',
                'show from', 'export', 'stats top', 'add haiku', 'delete haiku']
        self.assertEqual(good, values)
