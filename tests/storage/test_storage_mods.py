import unittest

from sqlalchemy import create_engine

from bot.storage.persistence import Persistence


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

    def test_put_mod(self):
        self.store.put_mod('carlos')
        self.assertEqual(self.store.get_mods(), ['carlos'])

    def test_put_multiple_mods(self):
        self.store.put_mod('carlos')
        self.store.put_mod('earl')
        self.store.put_mod('førl')
        self.assertEqual(self.store.get_mods(), ['carlos', 'earl', 'førl'])

    def test_put_remove_multiple_mods(self):
        self.store.put_mod('carlos')
        self.store.put_mod('earl')
        self.store.put_mod('førl')
        self.store.remove_mod('earl')
        self.assertEqual(self.store.get_mods(), ['carlos', 'førl'])

    def test_put_remove_single_mod(self):
        self.store.put_mod('førl')
        self.store.remove_mod('førl')
        self.assertEqual(self.store.get_mods(), ['There are currently no mods'])

    def test_is_mod(self):
        self.store.put_mod('førl')
        self.store.put_mod('pep')
        self.assertEqual(self.store.is_mod('pep'), True)
        self.assertEqual(self.store.is_mod('perp'), False)

    def test_is_mod_empty(self):
        self.assertEqual(self.store.is_mod('anything'), False)

    def test_super_mod(self):
        self.assertEqual(self.store.is_mod('karlos'), True)

    def test_is_not_mod_after_removed(self):
        self.store.put_mod('førl')
        self.store.put_mod('pep')
        self.store.remove_mod('førl')
        self.assertEqual(self.store.is_mod('førl'), False)
        self.assertEqual(self.store.is_mod('pep'), True)

    def test_add_multiple_and_delete(self):
        self.store.put_mod('one')
        self.store.put_mod('two')
        self.store.put_mod('three')
        self.store.put_mod('four')
        self.store.remove_mod('one')
        self.store.remove_mod('two')
        self.store.remove_mod('three')
        self.store.remove_mod('four')
        self.assertEqual(self.store.get_mods(), ['There are currently no mods'])
