import logging

from bot.commands.commands import Commands


def good_user(user):
    if user is None or len(user) < 3:
        return False
    return True


class CommandsParser:
    def __init__(self, store, slack):
        self.store = store
        self.slack = slack

    def handle_command(self, command, channel, action_user):
        logging.debug('Command {} recieved from channel {} by user {}'.format(command, channel, action_user))
        response = "Invalid command. Currently supported commands: " + str(Commands.values())

        if command.startswith(Commands.ADD_MOD.value):
            response = self._add_mod(command, action_user)
        elif command.startswith(Commands.REMOVE_MOD.value):
            response = self._remove_mod(command, action_user)
        elif command.startswith(Commands.LIST_MOD.value):
            response = self._list_mods()
        elif command.startswith(Commands.LAST_HAIKU.value):
            self._show_last_haiku(channel)
            return
        elif command.startswith(Commands.SHOW_FROM.value):
            self._show_from_haiku(command, channel)
            return
        elif command.startswith(Commands.SHOW_ID.value):
            self._show_id_haiku(command, channel)
            return

        self.slack.post_message(response, channel)

    def _add_mod(self, command, action_user):
        if not self.store.is_mod(action_user):
            logging.debug('User not mod')
            return "User '{}' is not a mod".format(action_user)

        user = command.replace(Commands.ADD_MOD.value, '').strip()
        if good_user(user):
            self.store.put_mod(user)
            return user + " added as bot mod."
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
        if len(clean) < 3:
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
