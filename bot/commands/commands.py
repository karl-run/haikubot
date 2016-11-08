from enum import Enum


class Commands(Enum):
    ADD_MOD = 'add mod'
    REMOVE_MOD = 'remove mod'
    LIST_MOD = 'list mod'
    LAST_HAIKU = 'show last'
    SHOW_ID = 'show'
    SHOW_FROM = 'show from'

    @staticmethod
    def values():
        return [e.value for e in Commands]
