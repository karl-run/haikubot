import json, time
from threading import Thread
import requests
import config

import bot.connectivity.haiku_parser as parser


def make_urls():
    flat_list = []
    url = config.STASH_URL if config.STASH_URL[len(config.STASH_URL) - 1] == '/' else config.STASH_URL + '/'
    for project in config.STASH_REPOSITORIES:
        for repo in project['REPOSITORIES']:
            flat_list.append(
                "{}rest/api/1.0/projects/{}/repos/{}/pull-requests".format(url, project['REPO_KEY'], repo)
            )

    return flat_list


def faux_response(url):
    return open(config.DEBUG_URL, 'r').read()


def fetch(url):
    if config.DEBUG:
        requests.get = faux_response  # Override get so we can serve a file

    response = requests.get(url)  # TODO add auth
    return json.loads(response)


class Stash(Thread):
    def __init__(self, post_func, store):
        Thread.__init__(self)
        self.alive = False
        self.post_func = post_func
        self.store = store
        self.urls = make_urls()

    def run(self):
        while self.alive:
            for url in self.urls:
                try:
                    result = fetch(url)
                except OSError:
                    print('Server not responding: ' + url)  # TODO add logging
                    continue

                parsed = parser.parse_stash_response(result, self.store)

                for haiku in parsed:
                    self.post_func(haiku['haiku'], haiku['author'])

            if self.alive:
                for _ in range(config.STASH_POLL_TIME):
                    time.sleep(1)

    def start(self, live=True):
        self.alive = live
        Thread.start(self)

    def stop(self):
        self.alive = False

    def is_alive(self):
        return self.alive
