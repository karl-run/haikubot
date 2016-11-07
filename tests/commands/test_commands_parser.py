import time
import unittest

from bot.commands.commands_parser import CommandsParser
from tests.utils.spy import Spy

ADD_VALID_CMD = "add mod valid_username"


class StashTest(unittest.TestCase):
    def setUp(self):
        store = type('Dummy', (object,), {})()
        slack = type('Dummy', (object,), {})()
        self.spy = Spy()
        self.cp = CommandsParser(store, slack)
        self.cp.fetch = lambda: {"values": []}

    def test_add_mod_no_permission(self):
        self.cp.store.is_mod = lambda x: False
        response = self.cp._add_mod(ADD_VALID_CMD, 'xXhac3rXx')

        self.assertEqual("User 'xXhac3rXx' is not a mod", response)

    def test_add_mod_with_permission(self):
        spy = Spy()
        self.cp.store.put_mod = spy.to_call
        self.cp.store.is_mod = lambda x: True
        self.cp._add_mod(ADD_VALID_CMD, 'good_user')

        self.assertTrue(spy.is_called())

    def test_add_mod_handle_no_user(self):
        spy = Spy()
        self.cp.store.put_mod = spy.to_call
        self.cp.store.is_mod = lambda x: True
        response = self.cp._add_mod('add mod yo', 'good_user')

        self.assertFalse(spy.is_called())
        self.assertEqual("'yo' is not a valid username.", response)

    def test_remove_mod_no_permission(self):
        self.cp.store.is_mod = lambda x: False
        response = self.cp._add_mod(ADD_VALID_CMD, 'xXhac3rBoiXx')

        self.assertEqual("User 'xXhac3rBoiXx' is not a mod", response)

    def test_remove_mod_with_permission(self):
        spy = Spy()
        self.cp.store.remove_mod = spy.to_call
        self.cp.store.is_mod = lambda x: True
        self.cp._remove_mod(ADD_VALID_CMD, 'good_user')

        self.assertTrue(spy.is_called())

    def test_remove_mod_handle_no_user(self):
        spy = Spy()
        self.cp.store.remove_mod = spy.to_call
        self.cp.store.is_mod = lambda x: True
        response = self.cp._remove_mod('remove mod', 'good_user')

        self.assertFalse(spy.is_called())
        self.assertEqual("'' is not a valid username.", response)

    def test_list_mods(self):
        self.cp.store.get_mods = lambda: ['moda', 'twoa']
        response = self.cp._list_mods()

        self.assertEqual("Current mods are: ['moda', 'twoa']", response)

    def test_show_last_haiku_empty(self):
        spy = Spy()
        self.cp.store.get_newest = lambda: (None, -1)
        self.cp.slack.post_message = spy.to_call
        self.cp._show_last_haiku('test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('There are no haikus!', 'test_channel'), spy.args)

    def test_show_last_haiku(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'mei', 'link': 'nei'}
        self.cp.store.get_newest = lambda: (haiku, 69)
        self.cp.slack.post_haiku = spy.to_call
        self.cp._show_last_haiku('test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('hai', 'mei', 69, 'nei', 'test_channel'), spy.args)
