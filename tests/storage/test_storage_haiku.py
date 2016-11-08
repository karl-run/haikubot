from sqlalchemy import create_engine

from bot.storage.persistence import Persistence

import unittest


class StorageHaikuTest(unittest.TestCase):
    store = None

    @classmethod
    def setUpClass(cls):
        cls.store = Persistence(db=create_engine('sqlite:///:memory:'))

    @classmethod
    def tearDownClass(cls):
        cls.store.connection.close()

    def tearDown(self):
        self.store._purge()

    def test_put_haiku_unposted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku1', 'Karl the Tester', posted=False)
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku1')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], False)

    def test_put_haiku_posted_false_default(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku2', 'Karl the Tester')
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku2')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], False)

    def test_get_newest_haiku(self):
        self.store.put_haiku('This is not a\nBad Boo!\nFakeu', 'Earl the Fester')
        self.store.put_haiku('This is an\nVery Cool\nHaiku3', 'Karl the Tester')
        haiku = self.store.get_newest()
        self.assertEqual(haiku[0]['haiku'], 'This is an\nVery Cool\nHaiku3')
        self.assertEqual(haiku[0]['author'], 'Karl the Tester')
        self.assertEqual(haiku[0]['posted'], False)

    def test_set_posted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku4', 'Karl the Tester', posted=False)
        self.store.set_posted(1)
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku4')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], True)

    def test_get_unposted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku5', 'Karl One', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku6', 'Carl Two', posted=True)
        self.store.put_haiku('This is an\nVery Cool\nHaiku7', 'Curl Three', posted=False)
        posted = self.store.get_unposted()
        self.assertEqual(posted[0]['author'], 'Karl One')
        self.assertEqual(posted[1]['author'], 'Curl Three')

    def test_get_haiku_by_author_default_amount(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku8', 'Karl One', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku9', 'Carl Two', posted=True)
        self.store.put_haiku('This is an\nVery Cool\nHaiku10', 'Karl Three', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku11', 'Karl Four', posted=False)
        posted = self.store.get_by('Karl')
        self.assertEqual(posted[0]['author'], 'Karl Four')
        self.assertTrue(len(posted) == 3)

    def test_get_haiku_by_author_set_amount(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku12', 'Karl One', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku13', 'Carl Two', posted=True)
        self.store.put_haiku('This is an\nVery Cool\nHaiku14', 'Karl Three', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku15', 'Karl Four', posted=False)
        posted = self.store.get_by('Karl', num=2)
        self.assertEqual(posted[0]['author'], 'Karl Four')
        self.assertEqual(posted[1]['author'], 'Karl Three')
        self.assertTrue(len(posted) == 2)
