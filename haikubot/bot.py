import logging
import time

from sqlalchemy.exc import IntegrityError
from websocket._exceptions import WebSocketException

from haikubot import config, VERSION
from haikubot.commands.commands_parser import CommandsParser
from haikubot.connectivity.slack import Slack
from haikubot.connectivity.stash import Stash
from haikubot.storage.persistence import Persistence


class Haikubot:
    def __init__(self, api_key):
        logging.info('Running haikubot v' + VERSION)

        self.slack = Slack(api_key)
        self.store = Persistence()
        self.stash = Stash(self._post_and_store_haiku, self.store)
        self.commands = CommandsParser(self.store, self.slack)
        self.bot_id = self.slack.get_id()

        self._at = '<@' + self.bot_id + '>'
        self.connectionInfo = {'died': False, 'channel': None, 'hasConnected': False}

    def run(self):
        try:
            self._connect_and_loop()
        except WebSocketException:
            logging.error("Websocket (slack) connection error, will try to reconnect in 30 seconds")
            time.sleep(30)
            self.run()
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
            self.connectionInfo['died'] = True
            self.run()

    def _post_and_store_haiku(self, haiku, author, link):
        try:
            eid = self.store.put_haiku(haiku, author, link)
        except IntegrityError:
            logging.info('haiku "{}" already exists.'.format(haiku))
            self.slack.post_message("It seems {} has posted a duplicate haiku.".format(author))
            return
        success = self.slack.post_haiku(haiku, author, eid, link)
        if success:
            self.store.set_posted(eid)

    def _connect_and_loop(self):
        logging.debug("Connecting to slack websocket...")
        if self.slack.connect():
            logging.info("Connected to slack websocket")
            self.connectionInfo['hasConnected'] = True

            if not self.stash.is_alive():
                self.stash.start()

            if self.connectionInfo['died'] and self.connectionInfo['channel']:
                response = "Fock you broke me. Don't do that again."
                self.slack.post_message(response, self.connectionInfo['channel'])

            while True:
                try:
                    command, channel, user = self._parse_slack_output(self.slack.read())
                except TimeoutError:
                    logging.error('Timed out while reading from Slack.')
                    continue

                if command and channel and user:
                    if user == 'haikubot':
                        continue

                    self.connectionInfo['channel'] = channel
                    self.commands.handle_command(command, channel, user)

                self.connectionInfo['channel'] = None

                time.sleep(config.READ_WEBSOCKET_DELAY)
        else:
            logging.error('Connection error, not able to connect to Slack.')
            if self.connectionInfo['hasConnected']:
                raise WebSocketException()
            raise ValueError('Unable to connect, bad token or bot ID?')

    def clean_up(self):
        self.stash.stop()

    def _parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self._at in output['text']:
                    return output['text'].split(self._at, 1)[1].strip(), \
                           output['channel'], \
                           self.slack.get_username(output['user'])
        return None, None, None
