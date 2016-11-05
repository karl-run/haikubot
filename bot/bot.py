import logging
import time
from enum import Enum

import config
from bot.connectivity.slack import Slack
from bot.connectivity.stash import Stash
from bot.storage.persistence import Persistence

READ_WEBSOCKET_DELAY = 1


class Commands(Enum):
    ADD_MOD = 'add mod'
    REMOVE_MOD = 'remove mod'
    LIST_MOD = 'list mod'
    TWEET = 'tweet'
    LAST_HAIKU = 'show last'
    SHOW_ID = 'show'

    @staticmethod
    def values():
        return [e.value for e in Commands]


class Haikubot:
    def __init__(self, api_key):
        self.slack = Slack(api_key)
        self.store = Persistence()
        self.stash = Stash(self.post_and_store_haiku, self.store)
        self.bot_id = self.slack.get_id()

        self._at = '<@' + self.bot_id + '>'
        self.death = {'died': False, 'channel': None}

    def run(self):
        try:
            if self.slack.connect():
                if not self.stash.is_alive():
                    self.stash.start()

                logging.info("haikubot connected and running!")
                if self.death['died'] and self.death['channel']:
                    response = "Fock you broke me. Don't do that again."
                    self.slack.post_message(response, self.death['channel'])
                while True:
                    try:
                        command, channel, user = self._parse_slack_output(self.slack.read())
                    except TimeoutError:
                        logging.error('Timed out while reading from Slack.')
                        continue

                    if command and channel and user:
                        self.death['channel'] = channel
                        self._handle_action(command, channel, user)

                    self.death['channel'] = None

                    time.sleep(READ_WEBSOCKET_DELAY)
            else:
                logging.error('Connection error, not able to connect to Slack.')
                raise ValueError('Unable to connect, bad token or bot ID?')

        except KeyboardInterrupt:
            self.stash.stop()
            logging.info("Stop has been called, trying to stop gracefully.")
        except ValueError:
            raise ValueError  # We want it to die
        except Exception:
            if config.DEBUG:
                logging.critical('config.DEBUG is set, crashing on failure.')
                raise Exception

            logging.error('Something unexpected happened, trying to restart bot.' + str(Exception))
            self.death['died'] = True
            self.run()

    def post_and_store_haiku(self, haiku, author, link):
        eid = self.store.put_haiku(haiku, author, link)
        success = self.slack.post_haiku(haiku, author, eid, link)
        if success:
            self.store.set_posted(eid)

    def _handle_action(self, command, channel, action_user):
        logging.debug('Command {} recieved from channel {} by user {}'.format(command, channel, action_user))
        response = "Invalid command. Currently supported commands: " + str(Commands.values())

        if self.store.is_mod(action_user):
            logging.debug('User has mod rights')
            if command.startswith(Commands.ADD_MOD.value):
                user = command.replace(Commands.ADD_MOD.value, '').strip()
                self.store.put_mod(user)
                response = user + " added as tweet-mod."
            if command.startswith(Commands.REMOVE_MOD.value):
                user = command.replace(Commands.REMOVE_MOD.value, '').strip()
                if self.store.is_mod(user):
                    self.store.remove_mod(user)
                    response = user + " has been removed as tweet-mod."
                else:
                    response = user + " isn't a tweet-mod."
            if command.startswith(Commands.TWEET.value):
                eid = command.replace(Commands.TWEET.value, '').strip()
                response = "// TODO implement this. But first we need some haikus :) Here's your input: " + eid

        if command.startswith(Commands.LIST_MOD.value):
            response = "Current mods are: " + str(self.store.get_mods())
        if command.startswith(Commands.LAST_HAIKU.value):
            newest, eid = self.store.get_newest()
            if newest is None:
                self.slack.post_message("There are no haikus!")
                return

            self.slack.post_haiku(newest['haiku'], newest['author'], eid, newest['link'], channel=channel)
            return
        if command.startswith(Commands.SHOW_ID.value):
            eid = command.replace(Commands.SHOW_ID.value, '').strip().replace('#', '')
            haiku = self.store.get(eid)
            if not haiku:
                response = 'Found no haiku with id {}'.format(eid)
            else:
                self.slack.post_haiku(haiku['haiku'], haiku['author'], eid, haiku['link'], channel=channel)
                return

        self.slack.post_message(response, channel)

    def _parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self._at in output['text']:
                    return output['text'].split(self._at)[1].strip().lower(), \
                           output['channel'], \
                           self.slack.get_username(output['user'])
        return None, None, None
