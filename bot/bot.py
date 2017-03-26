import logging
import time

from sqlalchemy.exc import IntegrityError

from bot.commands.commands_parser import CommandsParser
from bot.connectivity.slack import Slack
from bot.connectivity.stash import Stash
from bot.storage.persistence import Persistence

import config


class Haikubot:
    def __init__(self, api_key):
        self.slack = Slack(api_key)
        self.store = Persistence()
        self.stash = Stash(self.post_and_store_haiku, self.store)
        self.commands = CommandsParser(self.store, self.slack)
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
                        self.commands.handle_command(command, channel, user)

                    self.death['channel'] = None

                    time.sleep(config.READ_WEBSOCKET_DELAY)
            else:
                logging.error('Connection error, not able to connect to Slack.')
                raise ValueError('Unable to connect, bad token or bot ID?')

        except KeyboardInterrupt:
            self.stash.stop()
            logging.info("Stop has been called, trying to stop gracefully.")
        except ValueError:
            raise ValueError  # We want it to die
        except Exception as err:
            if config.DEBUG:
                logging.critical('config.DEBUG is set, crashing on failure, error: ' + str(err))
                raise Exception

            logging.error('Something unexpected happened, trying to restart bot.' + str(Exception))
            self.death['died'] = True
            self.run()

    def post_and_store_haiku(self, haiku, author, link):
        try:
            eid = self.store.put_haiku(haiku, author, link)
        except IntegrityError:
            logging.info('haiku "{}" already exists.'.format(haiku))
            self.slack.post_message("It seems {} has posted a duplicate haiku.".format(author))
            return
        success = self.slack.post_haiku(haiku, author, eid, link)
        if success:
            self.store.set_posted(eid)

    def _parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self._at in output['text']:
                    return output['text'].split(self._at)[1].strip(), \
                           output['channel'], \
                           self.slack.get_username(output['user'])
        return None, None, None
