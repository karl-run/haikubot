import logging

from slackclient import SlackClient

import config


class Slack:
    def __init__(self, api_key):
        self.sc = SlackClient(api_key)

    def post_message(self, message, channel=config.POST_TO_CHANNEL, as_user=True):
        if isinstance(message, list):
            return self.sc.api_call("chat.postMessage", channel=channel, as_user=as_user, attachments=message)

        return self.sc.api_call("chat.postMessage", channel=channel, as_user=as_user, text=message)

    def post_haiku(self, haiku, author, haiku_id, stash_link, channel=config.POST_TO_CHANNEL):
        haiku_to_post = haiku + " - " + author + "\n"
        title = 'Haiku #{}'.format(haiku_id)
        haiku_with_title = [{
            'fallback': '{}, {}'.format(title, haiku_to_post),
            'title': 'Haiku #{}'.format(haiku_id),
            'title_link': stash_link,
            'text': haiku_to_post
        }]
        logging.info('Posting haiku id {} to channel {}.'.format(haiku_id, channel))

        response = self.post_message(haiku_with_title, channel)

        if not response['ok']:
            logging.error('Unable to post haiku, error: {}'.format(response['error']))
        return response['ok']

    def connect(self):
        return self.sc.rtm_connect()

    def read(self):
        return self.sc.rtm_read()

    def get_username(self, uid):
        return self.sc.server.users.find(uid)
