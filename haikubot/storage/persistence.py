import logging
from datetime import datetime, timedelta
from functools import partial

import dateutil.parser
from sqlalchemy import create_engine
from sqlalchemy import func, Table, Column, Boolean, Integer, String, MetaData
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import select, update

from haikubot import config

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


def _is_within_weeks(weeks, haiku):
    date = dateutil.parser.parse(haiku.date)
    if date < datetime.now() - timedelta(weeks=weeks):
        return False
    return True


class Persistence:
    def __init__(self, db=None):
        if db is None:
            if config.FILE_DB:
                logging.info('Using file based SQLITE database: {}'.format(db_location))
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

    def put_haiku_model(self, haiku):
        hid = self.put_haiku(haiku.haiku, haiku.author, haiku.link)
        haiku.hid = hid
        return hid

    def put_haiku(self, haiku, author, link=None, posted=False, date=str(datetime.now())):
        logging.debug('Adding inserting haiku from user {}'.format(author))
        result = self.connection.execute(haikus.insert(), [{
            'haiku': haiku,
            'author': author,
            'posted': posted,
            'date': date,
            'link': link
        }])
        return result.inserted_primary_key[0]

    def get_unposted(self):
        return [row for row in self.connection.execute(select([haikus]).where(haikus.c.posted == False))]

    def set_posted(self, ids, posted=True):
        if type(ids) is not list:
            ids = [ids]

        logging.debug('Setting {} as posted={}'.format(str(ids), posted))
        for hid in ids:
            self.connection.execute(update(haikus).where(haikus.c.id == hid).values(posted=True))

    def get_haiku(self, hid):
        return self.connection.execute(
            select([haikus]).where(haikus.c.id == hid)
        ).first()

    def remove_haiku(self, hid):
        logging.debug('Deleting haiku #{}'.format(hid))
        return self.connection.execute(haikus.delete().where(haikus.c.id == hid))

    def get_newest(self):
        max_id = self.connection.execute(
            select([func.max(haikus.c.id)])
        ).scalar()

        return self.connection.execute(
            select([haikus]).where(haikus.c.id == max_id)
        ).first(), max_id

    def get_by(self, search, num=3):
        res = [row for row in self.connection.execute(
            select([haikus]).where(haikus.c.author.startswith(search + '%'))
        )]
        return res[:-num - 1:-1] if num != -1 else res

    def get_all_haiku(self):
        return [row for row in self.connection.execute(
            select([haikus])
        )]

    def get_all_haiku_weeks(self, weeks):
        return list(filter(partial(_is_within_weeks, weeks), [row for row in self.connection.execute(
            select([haikus])
        )]))

    def get_haiku_stats(self, top_num=None):
        logging.debug('Getting haiku stats with top {}'.format('everything' if top_num is not None else top_num))
        authors = [row[0] for row in self.connection.execute(select([haikus.c.author]).distinct())]
        stats = []
        for author in authors:
            stats.append((author, self.connection.execute(
                select([func.count(haikus.c.id)]).where(haikus.c.author == author)
            ).scalar()))

        stats.sort(key=lambda tup: tup[1], reverse=True)
        return stats[0:top_num]

    def put_mod(self, username):
        logging.debug('Adding {} as haikumod'.format(username))
        self.connection.execute(mods.insert(), [{
            'username': username,
        }])

    def remove_mod(self, username):
        logging.debug('Removing {} as haikumod'.format(username))
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

    def has_posted_haiku(self, name):
        authors = [row[0] for row in self.connection.execute(select([haikus.c.author]).distinct())]
        return name in authors

    def _purge(self):
        self.connection.execute(haikus.delete())
        self.connection.execute(checked.delete())
        self.connection.execute(mods.delete())
