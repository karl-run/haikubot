import unittest

import bot.connectivity.haiku_parser as parser
from tests.utils.spy import Spy


class HaikuParserTest(unittest.TestCase):
    def setUp(self):
        self.response = {
            'values': [
                {
                    'id': 12,
                    'description': "Glemte littegrann\r\ni kopier til utklipp.\r\nLa til tester og.\r\nDette hakke no med haiku å gjøre",
                    'author': {
                        'user': {
                            'displayName': 'Testesson'
                        }
                    },
                    'links': {'self': [{'href': 'https://stash.websait.tk/projects/TESTZ'}]}
                },
                {
                    'id': 13,
                    'description': "Dette er i hvert fall ikke et haiku",
                    'author': {
                        'user': {
                            'displayName': 'Glemmesson'
                        }
                    },
                    'links': {'self': [{'href': 'https://stash.websait.tk/projects/TESTZ'}]}
                }
            ]
        }

    def test_is_haiku(self):
        self.assertTrue(parser.is_haiku(self.response['values'][0]['description']))

    def test_non_haiku(self):
        self.assertFalse(parser.is_haiku(self.response['values'][1]['description']))

    def test_desc_to_haiku(self):
        result = parser.desc_to_haiku(self.response['values'][0]['description'],
                                      self.response['values'][0]['author'],
                                      self.response['values'][0]['links']['self'])
        wanted = {'haiku': "Glemte littegrann\ni kopier til utklipp.\nLa til tester og.\n", 'author': 'Testesson'}
        self.assertEqual(result['haiku'], wanted['haiku'])
        self.assertEqual(result['author'], wanted['author'])

    def test_parse_stash_response(self):
        result = parser.parse_stash_response(self.response, 'abc')
        wanted = {'haiku': "Glemte littegrann\ni kopier til utklipp.\nLa til tester og.\n", 'author': 'Testesson'}
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['haiku'], wanted['haiku'])
        self.assertEqual(result[0]['author'], wanted['author'])

    def test_parse_stash_response_skip_checked(self):
        store = type('Dummy', (object,), {})()
        store.is_checked = lambda x: True

        result = parser.parse_stash_response(self.response, 'abc', store)
        self.assertEqual(len(result), 0)

    def test_parse_stash_response_put_unchecked_in_store(self):
        stored_spy = Spy()
        store = type('Dummy', (object,), {})()
        store.is_checked = lambda x: False
        store.put_checked_id = stored_spy.to_call

        parser.parse_stash_response(self.response, 'abc', store)
        self.assertTrue(stored_spy.is_called())
