from bot.storage.persistence import Persistence
from tinydb.storages import MemoryStorage
from tinydb import TinyDB

import unittest


class StorageModsTest(unittest.TestCase):
    store = None

    @classmethod
    def setUpClass(cls):
        cls.store = Persistence(db=TinyDB(storage=MemoryStorage))

    @classmethod
    def tearDownClass(cls):
        cls.store.db.close()

    def tearDown(self):
        self.store._purge()

    def test_put_id(self):
        self.store.put_checked_id('649')
        self.assertTrue(self.store.is_checked('649'))

    def test_put_multiple_ids(self):
        self.store.put_checked_id('699')
        self.store.put_checked_id('12')
        self.store.put_checked_id('699292')
        self.assertTrue(self.store.is_checked('699'))
        self.assertTrue(self.store.is_checked('12'))
        self.assertTrue(self.store.is_checked('699292'))
