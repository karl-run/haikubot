from sqlalchemy import create_engine

from haikubot.utils.analyser import \
    get_longest_word_haiku, \
    get_most_words_haiku, \
    get_least_words_haiku, \
    _clean_haiku

import unittest


class StorageModsTest(unittest.TestCase):
    haiku_list = [
        {
            'id': 1,
            'haiku': "Glem te litt egrann\ni kop ier til utkl ipp.\nLa til tes ter og.\n",
            'author': "Test Testsson"
        },
        {
            'id': 2,
            'haiku': "Glemte ikke\ni kopier til ojveldiglangtord.\nLa til tester og.\n",
            'author': "Test Testsson"
        },
        {
            'id': 3,
            'haiku': "a b\nc d\ne f g\n",
            'author': "Test Testsson"
        }
    ]

    camel_case_haiku = {
        'id': 4,
        'haiku': "Hvis (detHarSkjeddFeil) {\n; ikkeVisEkstrateksten();\n} Ellers { visTeksten(); }\n",
        'author': "Test Testsson"
    }

    dirty_haiku = \
        {
            'id': 5,
            'haiku': "Takk for alt du sa ...\n ... Karl, takk for alt du ga, Karl\n Takk for all gledan\n",
            'author': "Test Testsson"
        }

    def test_longest_word(self):
        longest, word = get_longest_word_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 2)
        self.assertEqual(word, 'ojveldiglangtord')

    def test_most_words(self):
        longest, number, ids = get_most_words_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 1)
        self.assertEqual(number, 15)

    def test_fewest_words(self):
        longest, number, ids = get_least_words_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 3)
        self.assertEqual(number, 7)

    def test_camel_case(self):
        longest, word = get_longest_word_haiku([self.camel_case_haiku])
        self.assertEqual(word, 'Ekstrateksten')

    def test_clean_case(self):
        cleaned = _clean_haiku(self.dirty_haiku['haiku'])
        expected = ['Takk', 'for', 'alt', 'du', 'sa', 'Karl', 'takk', 'for', 'alt', 'du', 'ga', 'Karl', 'Takk', 'for', 'all', 'gledan']
        self.assertEqual(list(filter(len, cleaned.split(' '))), expected)
