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
    STATS_TIMELINE = 'stats timeline'
    ADD_HAIKU = 'add haiku'
    DELETE_HAIKU = 'delete haiku'
    WORDCLOUD = 'wordcloud'

    @staticmethod
    def values():
        return [e.value for e in Commands]

    @staticmethod
    def manpage():
        return """```
    1. show newest haiku:            @haikubot show last
    2. show specific haiku:          @haikubot show #69
    3. show all haiku from author:   @haikubot show from <author>
    4. show # haiku from author:     @haikubot show from <amount> <author>
    5. delete haiku (only for mods): @haikubot delete haiku #69
    6. add haiku manually:
        @haikubot add haiku
        haiku on line two
        three and four. Do remember
        author on line six
        Author Andersen
        Yes (only to confirm new authors)
    7. export all haikus:            @haikubot export
    8. export from specific user:    @haikubot export <author>
    9. show haiku statistics:        @haikubot stats top
   10. haiku with longest word:      @haikubot stats longest
   11. haiku with fewest words:      @haikubot stats fewest
   12. haiku with most words:        @haikubot stats most
   13. timeline stats:               @haikubot stats timeline
   14. timeline stats from sprint:   @haikubot stats timeline sprint
   15. wordcloud of all haiku:       @haikubot wordcloud
   16. wordcloud from single author: @haikubot wordcloud <author>
   17. wordcloud from sprint:        @haikubot wordcloud sprint
```"""
