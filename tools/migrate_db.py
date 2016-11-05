from sqlalchemy.exc import IntegrityError

from bot.storage.persistence import Persistence as PerNew
from bot.storage.persistence_legacy import Persistence as PerLegacy

if __name__ == "__main__":
    p_old = PerLegacy()
    p_new = PerNew()

    for haiku in p_old.haiku.all():
        try:
            p_new.put_haiku(haiku['haiku'], haiku['author'], haiku['link'], haiku['posted'])
        except IntegrityError:
            print('Error: Haiku already exists is database')

    old_mods = p_old.mods.all()
    if len(old_mods) > 0:
        for name in old_mods[0]['mods']:
            if not p_new.is_mod(name):
                p_new.put_mod(name)

    for old_checked in p_old.checked.all()[0]['cids']:
        if not p_new.is_checked(old_checked):
            p_new.put_checked_id(old_checked)
