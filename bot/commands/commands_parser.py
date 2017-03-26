import logging

from sqlalchemy.exc import IntegrityError

import config
from bot.commands.commands import Commands
from bot.model.haiku import Haiku
from bot.utils.color import string_to_color_hex
from bot.utils.haiku_parser import is_haiku


def good_user(user):
    if user is None or len(user) < 3:
        return False
    return True


class CommandsParser:
    def __init__(self, store, slack):
        self.store = store
        self.slack = slack

    def handle_command(self, command, channel, action_user):
        logging.debug('Command {} recieved from channel {} by user {} in channel {}'.format(command, channel,
                                                                                            action_user, channel))
        response = "Invalid command. Currently supported commands: " + str(Commands.values())

        if command.startswith(Commands.ADD_MOD.value):
            response = self._add_mod(command, action_user)
        elif command.startswith(Commands.REMOVE_MOD.value):
            response = self._remove_mod(command, action_user)
        elif command.startswith(Commands.LIST_MOD.value):
            response = self._list_mods()
        elif command.startswith(Commands.ADD_HAIKU.value):
            response = self._add_haiku(command, action_user)
        elif command.startswith(Commands.STATS_TOP.value):
            self._stats_top(command, channel)
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

        self.slack.post_message(response, channel)

    def _add_mod(self, command, action_user):
        if not self.store.is_mod(action_user):
            logging.debug('User not mod')
            return "User '{}' is not a mod".format(action_user)

        user = command.replace(Commands.ADD_MOD.value, '').strip()
        if good_user(user):
            try:
                self.store.put_mod(user)
            except IntegrityError:
                return "'{}' is already a mod".format(user)
            return "'{}' added as bot mod.".format(user)
        else:
            return "'{}' is not a valid username.".format(user)

    def _remove_mod(self, command, action_user):
        if not self.store.is_mod(action_user):
            logging.debug('User not mod')
            return "User '{}' is not a mod".format(action_user)

        user = command.replace(Commands.REMOVE_MOD.value, '').strip()
        if good_user(user):
            self.store.remove_mod(user)
            return user + " has been removed as bot mod."
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
            for h in haikus:
                self.slack.post_haiku(h['haiku'], h['author'], h['id'], h['link'], channel)
        else:
            self.slack.post_message('Found no haikus by "{}"'.format(search), channel)

    def _show_id_haiku(self, command, channel):
        eid = command.replace(Commands.SHOW_ID.value, '').strip().replace('#', '')
        try:
            eid = int(eid)
        except ValueError:
            self.slack.post_message('"{}" is not a valid number'.format(eid), channel)
            return
        haiku = self.store.get(eid)
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

    def _add_haiku(self, command, action_user):
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
                    return "{} tried posting a duplicate haiku, boo!".format(action_user.name)
                self.slack.post_haiku_model(haiku)
                return "{} just added haiku #{}.".format(action_user.name, haiku.hid)
            else:
                return "'{}' is not a valid author name".format(haiku_split[3])
        else:
            return "That's either not a valid haiku, or you forgot to supply and author. Remember to" \
                   " linebreak after the command, then supply 3 individual lines with the fourth line " \
                   "being the author.".format(haiku_string)
