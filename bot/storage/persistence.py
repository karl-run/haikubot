import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import func, Table, Column, Boolean, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, update, delete
from sqlalchemy.pool import StaticPool

import config

db_location = './haikubot.db' if not config.DATABASE_PATH else config.DATABASE_PATH + 'haikubot.db'

metadata = MetaData()
haikus = Table('haiku', metadata,
               Column('id', Integer, primary_key=True),
               Column('haiku', String, unique=True),
               Column('author', String),
               Column('posted', Boolean),
               Column('date', String),
               Column('link', String))

checked = Table('checked_posts', metadata,
                Column('id', Integer, primary_key=True),
                Column('stash_id', String, unique=True))

mods = Table('mods', metadata,
             Column('id', Integer, primary_key=True),
             Column('username', String, unique=True))


class Persistence:
    def __init__(self, db=None):
        if db is None:
            if config.FILE_DB:
                logging.info('Using file based SQLITE database')
                db = create_engine('sqlite:///{}'.format(db_location),
                                   connect_args={'check_same_thread': False},
                                   poolclass=StaticPool)
            else:
                logging.info('Connecting to remote {} database'.format(config.DB_ADAPTER))
                connection = '{}://{}:{}@{}'.format(config.DB_ADAPTER,
                                                    config.DB_USER,
                                                    config.DB_PW,
                                                    config.DB_URL)
                db = create_engine(connection, poolclass=StaticPool)
        else:
            logging.debug('Database engine provided.')

        self.db = db
        metadata.create_all(self.db)
        self.connection = self.db.connect()

    def put_checked_id(self, cid):
        logging.debug('Adding id {} to checked posts'.format(cid))
        self.connection.execute(checked.insert(), [{'stash_id': cid}])

    def is_checked(self, cid):
        return self.connection.execute(
            select([func.count(checked.c.stash_id)]).where(checked.c.stash_id == cid)
        ).scalar() == 1

    def put_haiku(self, haiku, author, link=None, posted=False):
        logging.debug('Adding inserting haiku from user {}'.format(author))
        result = self.connection.execute(haikus.insert(), [{
            'haiku': haiku,
            'author': author,
            'posted': posted,
            'date': str(datetime.now()),
            'link': link
        }])
        return result.inserted_primary_key

    def get_unposted(self):
        return [row for row in self.connection.execute(select([haikus]).where(haikus.c.posted == False))]

    def set_posted(self, ids, posted=True):
        if type(ids) is not list:
            ids = [ids]

        logging.debug('Setting {} as posted={}'.format(str(ids), posted))
        for hid in ids:
            self.connection.execute(update(haikus).where(haikus.c.id == hid).values(posted=True))

    def get(self, hid):
        return self.connection.execute(
            select([haikus]).where(haikus.c.id == hid)
        ).first()

    def get_newest(self):
        max_id = self.connection.execute(
            select([func.max(haikus.c.id)])
        ).scalar()

        return self.connection.execute(
            select([haikus]).where(haikus.c.id == max_id)
        ).first(), max_id

    def get_by(self, search, num=3):
        haiku_result = [row for row in self.connection.execute(
            select([haikus]).where(haikus.c.author.startswith(search + '%'))
        )]
        return haiku_result[0:num]

    def put_mod(self, username):
        logging.debug('Adding {} as mod'.format(username))
        self.connection.execute(mods.insert(), [{
            'username': username,
        }])

    def remove_mod(self, username):
        logging.debug('Removing {} as mod'.format(username))
        self.connection.execute(mods.delete().where(mods.c.username == username))

    def is_mod(self, username):
        if username == config.SUPER_MOD:
            return True

        return self.connection.execute(
            select([func.count(mods.c.id)]).where(mods.c.username == username)
        ).scalar() == 1

    def get_mods(self):
        all_mods = [str(row[1]) for row in self.connection.execute(select([mods]))]
        if not all_mods or len(all_mods) is 0:
            return ["There are currently no mods"]
        else:
            return all_mods

    def _purge(self):
        self.connection.execute(haikus.delete())
        self.connection.execute(checked.delete())
        self.connection.execute(mods.delete())
