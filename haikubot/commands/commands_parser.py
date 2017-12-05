import logging

from sqlalchemy.exc import IntegrityError

from haikubot import config
from haikubot.commands.commands import Commands
from haikubot.model.haiku import Haiku
from haikubot.utils.color import string_to_color_hex
from haikubot.utils.haiku_parser import is_haiku
from haikubot.utils.analyser import get_longest_word_haiku, get_most_words_haiku, get_least_words_haiku
from haikubot.utils.wordclouder import generate_cloud


def good_user(user):
    if user is None or len(user) < 3:
        return False
    return True


def dict_to_haiku(haiku_dict):
    return Haiku(haiku_dict['haiku'], haiku_dict['author'], haiku_dict['link'], haiku_dict['id'])


class CommandsParser:
    def __init__(self, store, slack):
        self.store = store
        self.slack = slack

    def handle_command(self, command, channel, action_user):
        logging.debug('Command {} recieved from channel {} by user {} in channel {}'.format(command, channel,
                                                                                            action_user, channel))
        response = "Invalid command. Currently supported commands: " + str(Commands.manpage())
        action_user = action_user.name

        if command.startswith(Commands.ADD_MOD.value):
            response = self._add_mod(command, action_user)
        elif command.startswith(Commands.REMOVE_MOD.value):
            response = self._remove_mod(command, action_user)
        elif command.startswith(Commands.LIST_MOD.value):
            response = self._list_mods()
        elif command.startswith(Commands.ADD_HAIKU.value):
            response = self._add_haiku(command, action_user, channel)
        elif command.startswith(Commands.DELETE_HAIKU.value):
            response = self._delete_haiku(command, action_user, channel)
        elif command.startswith(Commands.STATS_TOP.value):
            self._stats_top(command, channel)
            return
        elif command.startswith(Commands.STATS_LONGEST.value):
            self._stats_longest(channel)
            return
        elif command.startswith(Commands.STATS_MOST.value):
            self._stats_most(channel)
            return
        elif command.startswith(Commands.STATS_FEWEST.value):
            self._stats_fewest(channel)
            return
        elif command.startswith(Commands.LAST_HAIKU.value):
            self._show_last_haiku(channel)
            return
        elif command.startswith(Commands.SHOW_FROM.value):
            self._show_from_haiku(command, channel)
            return
        elif command.startswith(Commands.SHOW_ID.value):
            self._show_id_haiku(command, channel)
            return
        elif command.startswith(Commands.EXPORT.value):
            self._plain_export(command, channel)
            return
        elif command.startswith(Commands.WORDCLOUD.value):
            self._wordcloud(command, channel)
            return

        self.slack.post_message(response, channel)

    def _add_mod(self, command, action_user):
        if not self.store.is_mod(action_user):
            logging.debug('User not haikumod')
            return "User '{}' is not a haikumod".format(action_user)

        user = command.replace(Commands.ADD_MOD.value, '').strip()
        if good_user(user):
            try:
                self.store.put_mod(user)
            except IntegrityError:
                return "'{}' is already a haikumod".format(user)
            return "'{}' added as haikumod.".format(user)
        else:
            return "'{}' is not a valid username.".format(user)

    def _remove_mod(self, command, action_user):
        if not self.store.is_mod(action_user):
            logging.debug('User not haikumod')
            return "User '{}' is not a haikumod".format(action_user)

        user = command.replace(Commands.REMOVE_MOD.value, '').strip()
        if good_user(user):
            self.store.remove_mod(user)
            return user + " has been removed as haikumod."
        else:
            return "'{}' is not a valid username.".format(user)

    def _list_mods(self):
        return "Current mods are: " + str(self.store.get_mods())

    def _show_last_haiku(self, channel):
        newest, eid = self.store.get_newest()
        if newest is None:
            self.slack.post_message("There are no haikus!", channel)
            return

        self.slack.post_haiku(newest['haiku'], newest['author'], eid, newest['link'], channel)

    def _show_from_haiku(self, command, channel):
        clean = command.replace(Commands.SHOW_FROM.value, '').strip()
        if len(clean) <= 3:
            self.slack.post_message('"{}" is not descriptive enough'.format(clean), channel)
            return

        cmnds = clean.strip().split(' ')
        try:
            num = int(cmnds[0])
            search = ' '.join(cmnds[1:len(cmnds)])
        except ValueError:
            num = None
            search = ' '.join(cmnds[0:len(cmnds)])

        if num is None:
            haikus = self.store.get_by(search)
        else:
            haikus = self.store.get_by(search, num)

        if len(haikus) > 0:
            self.slack.post_haikus(haikus, channel)
        else:
            self.slack.post_message('Found no haikus by "{}"'.format(search), channel)

    def _show_id_haiku(self, command, channel):
        eid = command.replace(Commands.SHOW_ID.value, '').strip().replace('#', '')
        try:
            eid = int(eid)
        except ValueError:
            self.slack.post_message('"{}" is not a valid number'.format(eid), channel)
            return
        haiku = self.store.get_haiku(eid)
        if not haiku:
            self.slack.post_message('Found no haiku with id {}'.format(eid), channel)
        else:
            self.slack.post_haiku(haiku['haiku'], haiku['author'], eid, haiku['link'], channel)
            return

    def _stats_top(self, command, channel):
        num = command.replace(Commands.STATS_TOP.value, '').strip().replace('#', '')
        if len(num) < 1:
            num = None
        else:
            try:
                num = int(num)
            except ValueError:
                self.slack.post_message('"{}" is not a valid number'.format(num), channel)
                return

        stats = self.store.get_haiku_stats(num)
        if len(stats) < 1:
            self.slack.post_message("Couldn't find any haikus.", channel)
            return

        title = 'Haiku stats: # of haikus per user'
        attachments = [{
            'fallback': title,
            'title': title,
            'color': '#000000'
        }]
        for i in range(len(stats)):
            attachments.append({
                'text': "#{} with {} haiku: {}\n".format(i + 1, stats[i][1], stats[i][0]),
                'color': string_to_color_hex(stats[i][0])
            })

        self.slack.post_message(attachments, channel)

    def _stats_longest(self, channel):
        haikus = self.store.get_all_haiku()
        longest, word = get_longest_word_haiku(haikus)

        self.slack.post_message('Longest word in haiku: "{}"'.format(word), channel)
        self.slack.post_haiku_model(dict_to_haiku(self.store.get_haiku(longest.id)), channel=channel)

    def _stats_most(self, channel):
        haikus = self.store.get_all_haiku()
        longest, number, ids = get_most_words_haiku(haikus)

        self.slack.post_message('Most number of words in haiku: "{}", most recent:'.format(number), channel)
        self.slack.post_haiku_model(dict_to_haiku(self.store.get_haiku(longest.id)), channel=channel)
        if len(ids) > 0:
            self.slack.post_message('Older haikus with same amount of words: #{}'.format(', #'.join(str(i) for i in ids)), channel)
        else:
            self.slack.post_message('This is the only haiku with this number of words.', channel)

    def _stats_fewest(self, channel):
        haikus = self.store.get_all_haiku()
        longest, number, ids = get_least_words_haiku(haikus)

        self.slack.post_message('Least number of words in haiku: "{}"'.format(number), channel)
        self.slack.post_haiku_model(dict_to_haiku(self.store.get_haiku(longest.id)), channel=channel)
        if len(ids) > 0:
            self.slack.post_message('Older haikus with same amount of words: #{}'.format(', #'.join(str(i) for i in ids)), channel)
        else:
            self.slack.post_message('This is the only haiku with this number of words.', channel)

    def _plain_export(self, command, channel):
        search = command.replace(Commands.EXPORT.value, '').strip().replace('#', '')
        if len(search) < 1:
            logging.debug('Found no search parameter, exporting everything.')
            haikus = self.store.get_all_haiku()
        elif len(search) < 3:
            logging.debug('Found search parameter but not long enough, aborting.')
            self.slack.post_message('"{}" is not descriptive enough'.format(search), channel)
            return
        else:
            logging.debug('Found no search parameter, exporting everything.')
            haikus = self.store.get_by(search, num=-1)
            if len(haikus) < 1:
                self.slack.post_message('Found no haikus by "{}"'.format(search), channel)
                return

        export_max = config.GROUP_HAIKU_EXPORT_SIZE
        for c in range(0, len(haikus), export_max):
            haikus_simple = ""
            iteration_max = export_max if c + export_max < len(haikus) else len(haikus)
            for i in range(c, iteration_max):
                haikus_simple += "Haiku #{} by {}:\n".format(haikus[i]['id'], haikus[i]['author'])
                haikus_simple += haikus[i]['haiku']
                haikus_simple += '\n'

            self.slack.post_snippet(haikus_simple, channel)

    def _wordcloud(self, command, channel):
        search = command.replace(Commands.WORDCLOUD.value, '').strip().replace('#', '')
        is_sprint = search == 'sprint'
        if is_sprint:
            search = ''

        if len(search) < 1:
            logging.debug('Found no author, making wordcloud for everything.')
            if not is_sprint:
                haikus = self.store.get_all_haiku()
            else:
                haikus = self.store.get_all_haiku_weeks(4)
                if len(haikus) == 0:
                    self.slack.post_message("Couldn't find any haikus from the last 4 weeks.", channel)
                    return
            search = 'everyone'
        elif len(search) < 3:
            logging.debug('Found search parameter but not long enough, aborting.')
            self.slack.post_message('"{}" is not descriptive enough'.format(search), channel)
            return
        else:
            logging.debug('Found author, looking for haiku by {}.'.format(search))
            haikus = self.store.get_by(search, num=-1)
            if len(haikus) < 1:
                self.slack.post_message('Found no haikus by "{}"'.format(search), channel)
                return

        self.slack.post_message('Creating wordcloud from {} haiku.'.format(len(haikus)), channel)

        haiku_blob = ''.join([str(haiku['haiku']) for haiku in haikus])
        if search == 'everyone':
            image = generate_cloud(haiku_blob)
        else:
            image = generate_cloud(haiku_blob, string_to_color_hex(haikus[0]['author']))

        self.slack.post_image(image, search, channel)

    def _add_haiku(self, command, action_user, channel):
        haiku_string = command.replace(Commands.ADD_HAIKU.value, '').strip()
        haiku_split = haiku_string.replace('\r', '').split('\n')
        if len(haiku_split) > 3 and is_haiku(haiku_split[0:3]):
            haiku = Haiku('\n'.join(haiku_split[0:3]), haiku_split[3].title(), 'Slack')
            if len(haiku.author) > 8:
                if not self.store.has_posted_haiku(haiku.author):
                    if not (len(haiku_split) > 4 and haiku_split[4] == 'Yes'):
                        return "{} doesn't have any existing haiku, are you sure the name is" \
                               " correct? Repeat the request with a 'Yes' on a new line to verify,".format(haiku.author)
                try:
                    self.store.put_haiku_model(haiku)
                except IntegrityError:
                    return "{} tried posting a duplicate haiku, boo!".format(action_user)
                self.slack.post_haiku_model(haiku)
                if self.slack.get_channe_name(channel) != config.POST_TO_CHANNEL:
                    self.slack.post_message("{} just added haiku #{}.".format(action_user, haiku.hid))

                return "Added haiku #{}.".format(haiku.hid)
            else:
                return "'{}' is not a valid author name".format(haiku_split[3])
        else:
            return "That's either not a valid haiku, or you forgot to supply and author. Remember to" \
                   " linebreak after the command, then supply 3 individual lines with the fourth line " \
                   "being the author.".format(haiku_string)

    def _delete_haiku(self, command, action_user, channel):
        if not self.store.is_mod(action_user):
            logging.debug('User not mod')
            return "User '{}' is not a haikumod".format(action_user)

        hid = command.replace(Commands.DELETE_HAIKU.value, '').strip().replace('#', '')
        try:
            hid = int(hid)
        except ValueError:
            self.slack.post_message('"{}" is not a valid haiku id'.format(hid), channel)
            return

        deleted_haiku = self.store.get_haiku(hid)
        result = self.store.remove_haiku(hid)
        success = result.rowcount > 0

        if success:
            if self.slack.get_channe_name(channel) != config.POST_TO_CHANNEL:
                self.slack.post_message("User @{} just deleted haiku #{}:".format(action_user, hid))
                self.slack.post_haiku_model(dict_to_haiku(deleted_haiku))

            self.slack.post_haiku_model(dict_to_haiku(deleted_haiku), channel)
            return "Haiku #{} deleted. Say good bye to it one last time.".format(hid)

        return "There was no haiku with id #{}".format(hid)
