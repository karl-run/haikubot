import unittest

import bot.connectivity.haiku_parser as parser


class HaikuParserTest(unittest.TestCase):
    def setUp(self):
        self.response = {
            'values': [
                {
                    'description': "Glemte littegrann\r\ni kopier til utklipp.\r\nLa til tester og.\r\nDette hakke no med haiku å gjøre",
                    'author': {
                        'user': {
                            'displayName': 'Testesson'
                        }
                    }
                },
                {
                    'description': "Dette er i hvert fall ikke et haiku",
                    'author': {
                        'user': {
                            'displayName': 'Glemmesson'
                        }
                    }
                }
            ]
        }

    def test_is_haiku(self):
        self.assertTrue(parser.is_haiku(self.response['values'][0]['description']))

    def test_non_haiku(self):
        self.assertFalse(parser.is_haiku(self.response['values'][1]['description']))

    def test_desc_to_haiku(self):
        result = parser.desc_to_haiku(self.response['values'][0]['description'], self.response['values'][0]['author'])
        wanted = {'haiku': "> Glemte littegrann\n> i kopier til utklipp.\n> La til tester og.\n", 'author': 'Testesson'}
        self.assertEqual(result['haiku'], wanted['haiku'])
        self.assertEqual(result['author'], wanted['author'])

    def test_parse_stash_response(self):
        result = parser.parse_stash_response(self.response)
        wanted = {'haiku': "> Glemte littegrann\n> i kopier til utklipp.\n> La til tester og.\n", 'author': 'Testesson'}
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['haiku'], wanted['haiku'])
        self.assertEqual(result[0]['author'], wanted['author'])


if __name__ == '__main__':
    unittest.main()
