from datetime import datetime

from tinydb import TinyDB, where


class Persistence:
    def __init__(self, db=TinyDB('store.json')):
        self.db = db
        self.haiku = self.db.table('haiku')
        self.mods = self.db.table('mod')
        self.max_haiku_id = len(self.haiku)

    def put_haiku(self, haiku, author, posted=True):
        self.haiku.insert(
            {
                'haiku': haiku,
                'author': author,
                'date': str(datetime.now()),
                'posted': posted
            }
        )
        self.max_haiku_id += 1

    def get_unposted(self):
        return self.haiku.search(where('posted') == False)

    def set_posted(self, ids, posted=True):
        if type(ids) is not list:
            ids = [ids]

        self.haiku.update({'posted': posted}, eids=ids)

    def get(self, eid):
        return self.haiku.get(eid=eid)

    def get_newest(self):
        return self.haiku.get(eid=self.max_haiku_id)

    def put_mod(self, username):
        if len(self.mods) < 1:
            self.mods.insert({'mods': [username]})
            return

        previous_mods = self.mods.get(eid=1)['mods']
        self.mods.update({'mods': [*previous_mods, username]}, eids=[1])

    def remove_mod(self, username):
        previous_mods = self.mods.get(eid=1)['mods']
        if len(previous_mods) == 1:
            self.mods.remove(eids=[1])
            return

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
        self.haiku.purge()
        self.mods.purge()