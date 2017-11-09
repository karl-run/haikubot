from enum import Enum


class Commands(Enum):
    ADD_MOD = 'add mod'
    REMOVE_MOD = 'remove mod'
    LIST_MOD = 'list mod'
    LAST_HAIKU = 'show last'
    SHOW_ID = 'show'
    SHOW_FROM = 'show from'
    EXPORT = 'export'
    STATS_TOP = 'stats top'
    STATS_LONGEST = 'stats longest'
    STATS_FEWEST = 'stats fewest'
    STATS_MOST = 'stats most'
    ADD_HAIKU = 'add haiku'
    DELETE_HAIKU = 'delete haiku'

    @staticmethod
    def values():
        return [e.value for e in Commands]

    @staticmethod
    def manpage():
        return """```
    1. show newest haiku:            @haikubot show last
    2. show specific haiku:          @haikubot show #69
    3. show all haiku from author:   @haikubot show from <author>
    4. delete haiku (only for mods): @haikubot delete haiku #69
    5. add haiku manually:
        @haikubot add haiku
        haiku on lines
        three to five and remember
        add author on six
        Author Andersen
        Yes (only to confirm new authors)
    6. export all haikus:            @haikubot export
    7. export from specific user:    @haikubot export <author>
    8. show haiku statistics:        @haikubot stats top
    9. haiku with longest word:      @haikubot stats longest
   10. haiku with fewest words:      @haikubot stats fewest
   11. haiku with most words:        @haikubot stats most
```"""
