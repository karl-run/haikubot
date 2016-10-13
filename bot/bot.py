import json
import time
import traceback
from enum import Enum

import requests
from slackclient import SlackClient

from bot.storage.persistence import Persistence
from bot.connectivity.stash import Stash

READ_WEBSOCKET_DELAY = 1


class Commands(Enum):
    ADD_MOD = 'add mod'
    REMOVE_MOD = 'remove mod'
    LIST_MOD = 'list mod'
    TWEET = 'tweet'
    DANIEL = 'daniel'
    LAST_HAIKU = 'show last'

    @staticmethod
    def values():
        return [e.value for e in Commands]


class Haikubot:
    def __init__(self, api_key, bot_id):
        self.client = SlackClient(api_key)  # TODO pull this out to a seperate class
        self.store = Persistence()
        self.stash = Stash(self.post_haiku, self.store)

        self.id = bot_id
        self._at = '<@' + bot_id + '>'
        self.death = {'died': False, 'channel': None}
        self.seconds = 0

        self.stash.start()

    def post_haiku(self, haiku, author, channel='haikubot-test'):
        haiku_to_post = haiku + " - " + author + "\n"
        response = self.client.api_call("chat.postMessage", channel=channel, text=haiku_to_post, as_user=True)
        success = response is not None
        self.store.put_haiku(haiku, author, posted=success)

    def run(self):
        try:
            if self.client.rtm_connect():
                print("haikubot connected and running!")
                if self.death['died'] and self.death['channel']:
                    response = "Fock you broke me. Don't do that again."
                    self.client.api_call("chat.postMessage", channel=self.death['channel'], text=response, as_user=True)
                while True:
                    command, channel, user = self._parse_slack_input(self.client.rtm_read())
                    if command and channel and user:
                        self.death['channel'] = channel
                        self._handle_action(command, channel, user)
                    time.sleep(READ_WEBSOCKET_DELAY)
                    self.death['channel'] = None
                    self.seconds += 1
                    if self.seconds > 3600:
                        self.post_joke()
                        self.seconds = 0
            else:
                print("Connection failed. Invalid Slack token or bot ID?")
        except KeyboardInterrupt:
            self.stash.stop()
            print("Trying to stop gracefully..")
        except:
            traceback.print_last()
            self.death['died'] = True
            self.run()

    def _handle_action(self, command, channel, action_user):
        response = "Invalid command. Currently supported commands: " + str(Commands.values())

        if self.store.is_mod(action_user):
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
        if command.startswith(Commands.DANIEL.value):
            response = "Daniel is a focker"
        if command.startswith(Commands.LAST_HAIKU.value):
            newest = self.store.get_newest()
            self.post_haiku(newest['haiku'], newest['author'], channel)
            return

        self.client.api_call("chat.postMessage", channel=channel,
                             text=response, as_user=True)

    def _parse_slack_input(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self._at in output['text']:
                    return output['text'].split(self._at)[1].strip().lower(), output[
                        'channel'], self.client.server.users.find(output['user'])
        return None, None, None

    def post_joke(self):
        url = "http://tambal.azurewebsites.net/joke/random"
        response = requests.get(url)
        parsed = json.loads(response.text)['joke']
        self.client.api_call("chat.postMessage", channel='haikubot-test', text=parsed, as_user=True)
