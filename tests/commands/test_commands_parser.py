import unittest
from collections import namedtuple

from haikubot.commands.commands import Commands
from haikubot.commands.commands_parser import CommandsParser
from tests.utils.spy import Spy

ActionUser = namedtuple('ActionUser', 'name')

ADD_VALID_CMD = "add mod valid_username"
TESTBOY = ActionUser(name='testboy')


class CommandParserTest(unittest.TestCase):
    def setUp(self):
        store = type('Dummy', (object,), {})()
        slack = type('Dummy', (object,), {})()
        self.spy = Spy()
        self.cp = CommandsParser(store, slack)
        self.cp.fetch = lambda: {"values": []}

    def test_add_mod_no_permission(self):
        self.cp.store.is_mod = lambda x: False
        response = self.cp._add_mod(ADD_VALID_CMD, 'xXhac3rXx')

        self.assertEqual("User 'xXhac3rXx' is not a haikumod", response)

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
        response = self.cp._remove_mod(ADD_VALID_CMD, 'xXhac3rBoiXx')

        self.assertEqual("User 'xXhac3rBoiXx' is not a haikumod", response)

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

    def test_show_last_id_haiku_invalid(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp._show_id_haiku('show #lol', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('"lol" is not a valid number', 'test_channel'), spy.args)

    def test_show_last_id_haiku_not_found(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp.store.get_haiku = lambda x: None
        self.cp._show_id_haiku('show #69', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('Found no haiku with id 69', 'test_channel'), spy.args)

    def test_show_last_id_haiku(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'mei', 'link': 'nei'}
        self.cp.store.get_haiku = lambda x: haiku
        self.cp.slack.post_haiku = spy.to_call
        self.cp._show_id_haiku('show #69', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('hai', 'mei', 69, 'nei', 'test_channel'), spy.args)

    def test_show_from_haiku_too_short(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp._show_from_haiku('show from kar', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('"kar" is not descriptive enough', 'test_channel'), spy.args)

    def test_show_from_haiku_with_number(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'mei', 'link': 'nei', 'id': 3}
        self.cp.store.get_by = lambda x, n: [haiku, haiku]
        self.cp.slack.post_haikus = spy.to_call
        self.cp._show_from_haiku('show from 3 carl', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertTrue(spy.is_called_times(1))
        self.assertEqual(([haiku, haiku], 'test_channel'), spy.args)

    def test_show_from_haiku_no_number(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'mei', 'link': 'nei', 'id': 3}
        self.cp.store.get_by = lambda x: [haiku, haiku, haiku]
        self.cp.slack.post_haikus = spy.to_call
        self.cp._show_from_haiku('show from carl', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertTrue(spy.is_called_times(1))
        self.assertEqual(([haiku, haiku, haiku], 'test_channel'), spy.args)

    def test_show_from_haiku_none_found(self):
        spy = Spy()
        false_spy = Spy()
        self.cp.store.get_by = lambda x, n: []
        self.cp.slack.post_message = spy.to_call
        self.cp.slack.post_haiku = spy.to_call
        self.cp._show_from_haiku('show from 2 carl', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertFalse(false_spy.is_called())
        self.assertTrue(false_spy.is_called_times(0))
        self.assertEqual(('Found no haikus by "carl"', 'test_channel'), spy.args)

    def test_haiku_stats_valid(self):
        spy = Spy()
        self.cp.store.get_haiku_stats = lambda x: [('Karl', 23), ('Dan', 3)]
        self.cp.slack.post_message = spy.to_call
        self.cp._stats_top('stats top', 'test_channel')

        good = ([{'color': '#000000', 'title': 'Haiku stats: # of haikus per user',
                  'fallback': 'Haiku stats: # of haikus per user'},
                 {'color': '#75235e', 'text': '#1 with 23 haiku: Karl\n'},
                 {'color': '#c249c7', 'text': '#2 with 3 haiku: Dan\n'}],
                'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(good, spy.args)

    def test_haiku_stats_valid_limit_top(self):
        spy = Spy()
        self.cp.store.get_haiku_stats = lambda x: [('Karl', 23)]
        self.cp.slack.post_message = spy.to_call
        self.cp._stats_top('stats top 1', 'test_channel')

        good = ([{'color': '#000000', 'title': 'Haiku stats: # of haikus per user',
                  'fallback': 'Haiku stats: # of haikus per user'},
                 {'color': '#75235e', 'text': '#1 with 23 haiku: Karl\n'}],
                'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(good, spy.args)

    def test_haiku_stats_valid_bad_limit(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp._stats_top('stats top kek', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('"kek" is not a valid number', 'test_channel'), spy.args)

    def test_haiku_stats_valid_empty_result(self):
        spy = Spy()
        self.cp.store.get_haiku_stats = lambda x: []
        self.cp.slack.post_message = spy.to_call
        self.cp._stats_top('stats top 1', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(("Couldn't find any haikus.", "test_channel"), spy.args)

    def test_haiku_plain_export_not_found(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp.store.get_by = lambda x, num: []
        self.cp._plain_export('export wakaka', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('Found no haikus by "wakaka"', "test_channel"), spy.args)

    def test_haiku_plain_export(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'mei', 'link': 'nei', 'id': 3}
        self.cp.slack.get_channel_info = lambda x: {'error': 'channel_not_found'}
        self.cp.store.get_all_haiku = lambda: [haiku]
        self.cp.slack.post_snippet = spy.to_call
        self.cp._plain_export('export', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('Haiku #3 by mei:\nhai\n', "test_channel"), spy.args)

    def test_haiku_plain_export_with_search(self):
        spy = Spy()
        haiku = {'haiku': 'hai', 'author': 'nei', 'link': 'nei', 'id': 3}
        self.cp.slack.get_channel_info = lambda x: {'error': 'channel_not_found'}
        self.cp.store.get_by = lambda x, num: [haiku]
        self.cp.slack.post_snippet = spy.to_call
        self.cp._plain_export('export nok', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('Haiku #3 by nei:\nhai\n', "test_channel"), spy.args)

    def test_haiku_plain_export_with_search_bad(self):
        spy = Spy()
        self.cp.slack.get_channel_info = lambda x: {'error': 'channel_not_found'}
        self.cp.slack.post_message = spy.to_call
        self.cp._plain_export('export ka', 'test_channel')

        self.assertTrue(spy.is_called())
        self.assertEqual(('"ka" is not descriptive enough', "test_channel"), spy.args)

    def test_handle_command_invalid(self):
        spy = Spy()
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('not good command', 'test_channel', TESTBOY)

        good = "Invalid command. Currently supported commands: " + str(Commands.values())

        self.assertTrue(spy.is_called())
        self.assertEqual((good, 'test_channel'), spy.args)

    def test_handle_command_add_mod(self):
        spy = Spy()
        self.cp._add_mod = spy.to_call
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('add mod', 'test_channel', TESTBOY)

        self.assertTrue(spy.times_called == 2)
        self.assertTrue(spy.is_called())

    def test_handle_command_remove_mod(self):
        spy = Spy()
        self.cp._remove_mod = spy.to_call
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('remove mod', 'test_channel', TESTBOY)

        self.assertTrue(spy.times_called == 2)
        self.assertTrue(spy.is_called())

    def test_handle_command_list_mod(self):
        spy = Spy()
        self.cp._list_mods = spy.to_call
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('list mod', 'test_channel', TESTBOY)

        self.assertTrue(spy.times_called == 2)
        self.assertTrue(spy.is_called())

    def test_handle_command_stats_top(self):
        spy = Spy()
        false_spy = Spy()
        self.cp._stats_top = spy.to_call
        self.cp.slack.post_message = false_spy.to_call
        self.cp.handle_command('stats top', 'test_channel', TESTBOY)

        self.assertFalse(false_spy.is_called())
        self.assertTrue(spy.is_called())

    def test_handle_command_last_haiku(self):
        spy = Spy()
        false_spy = Spy()
        self.cp._show_last_haiku = spy.to_call
        self.cp.slack.post_message = false_spy.to_call
        self.cp.handle_command('show last', 'test_channel', TESTBOY)

        self.assertFalse(false_spy.is_called())
        self.assertTrue(spy.is_called())

    def test_handle_command_haiku_from(self):
        spy = Spy()
        false_spy = Spy()
        self.cp._show_from_haiku = spy.to_call
        self.cp.slack.post_message = false_spy.to_call
        self.cp.handle_command('show from', 'test_channel', TESTBOY)

        self.assertFalse(false_spy.is_called())
        self.assertTrue(spy.is_called())

    def test_handle_command_show_haiku_id(self):
        spy = Spy()
        false_spy = Spy()
        self.cp._show_id_haiku = spy.to_call
        self.cp.slack.post_message = false_spy.to_call
        self.cp.handle_command('show', 'test_channel', TESTBOY)

        self.assertFalse(false_spy.is_called())
        self.assertTrue(spy.is_called())

    def test_handle_command_add_haiku(self):
        spy = Spy()
        self.cp._add_haiku = spy.to_call
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('add haiku bla bla', 'test_channel', TESTBOY)

        self.assertEqual(2, spy.times_called)
        self.assertTrue(spy.is_called())

    def test_handle_command_delete_haiku(self):
        spy = Spy()
        self.cp._delete_haiku = spy.to_call
        self.cp.slack.post_message = spy.to_call
        self.cp.handle_command('delete haiku #69', 'test_channel', TESTBOY)

        self.assertEqual(2, spy.times_called)
        self.assertTrue(spy.is_called())
