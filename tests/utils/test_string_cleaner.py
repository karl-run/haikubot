from haikubot.utils.string_cleaner import clean_words, clean_characters, camel_case_clean

import unittest


class StorageModsTest(unittest.TestCase):
    def test_clean_words(self):
        clean = clean_words('Dette er en lang streng med mange er er er som ikke skal være med.')
        self.assertEqual(clean, 'dette lang streng mange være .')

    def test_clean_characters(self):
        clean = clean_characters('Dette er en lang streng, med komma, rare tegn {lol} og litt annet...')
        self.assertEqual(clean, 'Dette er en lang streng med komma rare tegn lol og litt annet ')

    def test_split_camelcase(self):
        clean = camel_case_clean('En lang setning medNoeCamelCaseGreier, hvorforDetDa?')
        self.assertEqual(clean, 'En lang setning med Noe Camel Case Greier, hvorfor Det Da?')
