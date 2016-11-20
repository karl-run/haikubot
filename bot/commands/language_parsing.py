import json
import uuid

import requests

import config

VERSION = 20161020


def _build_dumb_string(response):
    # This could probably have been done a bit cleaner.
    dumb = response['action'].replace('_', ' ') + ' '
    if 'number' in response['parameters']:
        dumb += response['parameters']['number'] + ' '
    if 'name' in response['parameters']:
        if 'amount' in response['parameters']:
            dumb += response['parameters']['amount'] + ' '
        dumb += response['parameters']['name']
    return dumb

class ApiAi:
    URL = "https://api.api.ai/v1/query?v={}&lang=en".format(VERSION)
    HEADER = {'Authorization': 'Bearer {}'}

    def __init__(self):
        self.URL += "&sessionId={}".format(uuid.uuid1())
        self.HEADER['Authorization'] = self.HEADER['Authorization'].format(config.API_AI_TOKEN)
        pass

    def process(self, command):
        get_url = self.URL + "&query={}".format(command)
        response = self.fetch(get_url)
        success = response['status']['errorType'] == 'success'
        fulfillment = response['result']['fulfillment']
        if 'speech' in fulfillment and len(fulfillment['speech']) > 1:
            return fulfillment['speech'], False
        if success:
            return _build_dumb_string(response['result']), success
        return "", False

    def fetch(self, url):
        response = requests.get(url, headers=self.HEADER)
        return json.loads(response.text)
