from bot.storage.persistence import Persistence
from tinydb.storages import MemoryStorage
from tinydb import TinyDB

import unittest


class StorageHaikuTest(unittest.TestCase):
    store = None

    @classmethod
    def setUpClass(cls):
        cls.store = Persistence(db=TinyDB(storage=MemoryStorage))

    @classmethod
    def tearDownClass(cls):
        cls.store.db.close()

    def tearDown(self):
        self.store._purge()

    def test_put_haiku_unposted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Karl the Tester', posted=False)
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], False)

    def test_put_haiku_posted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Karl the Tester')
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], True)

    def test_get_newest_haiku(self):
        self.store.put_haiku('This is not a\nBad Boo!\nFakeu', 'Earl the Fester')
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Karl the Tester')
        haiku = self.store.get_newest()
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], True)

    def test_set_posted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Karl the Tester', posted=False)
        self.store.set_posted(1)
        haiku = self.store.get(1)
        self.assertEqual(haiku['haiku'], 'This is an\nVery Cool\nHaiku')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], True)

    def test_get_unposted(self):
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Karl One', posted=False)
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Carl Two', posted=True)
        self.store.put_haiku('This is an\nVery Cool\nHaiku', 'Curl Three', posted=False)
        posted = self.store.get_unposted()
        self.assertEqual(posted[0]['author'], 'Karl One')
        self.assertEqual(posted[1]['author'], 'Curl Three')
