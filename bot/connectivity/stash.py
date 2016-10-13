import json, time
from threading import Thread
import requests

import bot.connectivity.haiku_parser as parser

URL = "bot/connectivity/example_stash.json"
WAIT = 2


class Stash(Thread):
    def __init__(self, post_func, store):
        Thread.__init__(self)
        self.alive = True
        self.post_func = post_func
        self.store = store

    def run(self):
        while self.alive:
            result = self.fetch()
            parsed = parser.parse_stash_response(result, self.store)

            for haiku in parsed:
                self.post_func(haiku['haiku'], haiku['author'])

            if self.alive:
                time.sleep(WAIT)

    def start(self, live=True):
        Thread.start(self)
        self.alive = live

    def stop(self):
        self.alive = False

    def fetch(self):
        # TODO replace with actual REST-call
        response = open(URL, 'r').read()
        return json.loads(response)
