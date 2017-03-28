from sqlalchemy import create_engine

from haikubot.storage.persistence import Persistence

import unittest


class StorageModsTest(unittest.TestCase):
    store = None

    @classmethod
    def setUpClass(cls):
        cls.store = Persistence(db=create_engine('sqlite:///:memory:'))

    @classmethod
    def tearDownClass(cls):
        cls.store.connection.close()

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

    def test_is_checked_empty(self):
        self.assertFalse(self.store.is_checked('69'))
