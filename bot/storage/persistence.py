import logging
from datetime import datetime

from tinydb import Query
from tinydb import TinyDB, where

import config

db_location = 'store.json' if not config.DATABASE_PATH else config.DATABASE_PATH + 'store.json'


class Persistence:
    def __init__(self, db=TinyDB(db_location)):
        self.db = db
        self.haiku = self.db.table('haiku')
        self.mods = self.db.table('mod')
        self.checked = self.db.table('checked_posts')
        self.max_haiku_id = len(self.haiku)

    def put_checked_id(self, cid):
        if len(self.checked) < 1:
            self.checked.insert({'cids': [cid]})
            return

        logging.debug('Adding id {} to checked posts'.format(cid))
        checked_ids = self.checked.get(eid=1)['cids']
        self.checked.update({'cids': [*checked_ids, cid]}, eids=[1])

    def is_checked(self, cid):
        if len(self.checked) < 1:
            return False

        return cid in self.checked.get(eid=1)['cids']

    def put_haiku(self, haiku, author, link, posted=False):
        logging.debug('Adding inserting haiku from user {}'.format(author))
        eid = self.haiku.insert(
            {
                'haiku': haiku,
                'author': author,
                'date': str(datetime.now()),
                'posted': posted,
                'link': link
            }
        )
        self.max_haiku_id += 1
        return eid

    def get_unposted(self):
        return self.haiku.search(where('posted') == False)

    def set_posted(self, ids, posted=True):
        if type(ids) is not list:
            ids = [ids]

        logging.debug('Setting {} as posted={}'.format(str(ids), posted))
        self.haiku.update({'posted': posted}, eids=ids)

    def get(self, eid):
        return self.haiku.get(eid=int(eid))

    def get_newest(self):
        return self.haiku.get(eid=self.max_haiku_id), self.max_haiku_id

    def get_by(self, search, num=3):
        haiku_query = Query()
        kek = self.haiku.search(haiku_query.author.test(lambda name: search.lower() in name.lower()))
        print(kek)
        return self.haiku.search(haiku_query.author.test(lambda name: search.lower() in name.lower()))[0:num]

    def put_mod(self, username):
        if len(self.mods) < 1:
            self.mods.insert({'mods': [username]})
            return

        logging.debug('Adding {} as mod'.format(username))
        previous_mods = self.mods.get(eid=1)['mods']
        self.mods.update({'mods': [*previous_mods, username]}, eids=[1])

    def remove_mod(self, username):
        previous_mods = self.mods.get(eid=1)['mods']
        if len(previous_mods) == 1:
            self.mods.remove(eids=[1])
            return

        logging.debug('Removing {} as mod'.format(username))
        previous_mods.remove(username)
        self.mods.update({'mods': [*previous_mods]}, eids=[1])

    def is_mod(self, username):
        if username == 'karlos':
            return True

        if len(self.mods) < 1:
            return False

        return username in self.mods.get(eid=1)['mods']

    def get_mods(self):
        none = False
        if len(self.mods) < 1:
            none = True

        mods = self.mods.get(eid=1)
        if not mods or none:
            return ["There are currently no mods"]
        else:
            return mods['mods']

    def _purge(self):
        logging.critical('Deleting all tables')
        self.haiku.purge()
        self.mods.purge()
        self.checked.purge()
