import unittest
import time

from bot.connectivity.stash import Stash
from tests.utils.spy import Spy


class StashTest(unittest.TestCase):
    def setUp(self):
        self.spy = Spy()
        self.stash = Stash(self.spy.to_call, None)
        self.stash.fetch = lambda: {"values": []}

    def tearDown(self):
        self.stash.stop()
        self.spy = None

    def test_fetch(self):
        self.stash.start(False)
        time.sleep(0.1)
        self.assertTrue(not self.spy.is_called())
