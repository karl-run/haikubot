from sqlalchemy import create_engine

from haikubot.utils.analyser import get_longest_word_haiku, get_most_words_haiku, get_least_words_haiku

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

    def test_longest_word(self):
        longest, word = get_longest_word_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 2)
        self.assertEqual(word, 'ojveldiglangtord')

    def test_most_words(self):
        longest, number = get_most_words_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 1)
        self.assertEqual(number, 15)


    def test_fewest_words(self):
        longest, number = get_least_words_haiku(self.haiku_list)
        self.assertEqual(longest['id'], 3)
        self.assertEqual(number, 7)
